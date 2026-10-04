import asyncio
import hashlib
import json
from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.messages import HumanMessage
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from config import REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY, settings
from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry
from src.core.logging_config import setup_logging
from src.core.rate_limiter import (check_and_consume_daily_budget,
                                   check_rate_limit)
from src.core.redis_client import redis_client
from src.core.streaming_callback import StreamingProgressCallback

load_dotenv()
logger = setup_logging(
    log_level=settings.log_level,
    render_json=settings.env == "production",
)


app = FastAPI()

allowed_origins: List[str] = [
    o.strip() for o in settings.allowed_origins.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=2000)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    try:
        redis_client.ping()
    except Exception as e:
        logger.warning("readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest, http_request: Request):
    client_ip = http_request.client.host if http_request.client else "unknown"
    logger.info(
        "analyze request received", user_input=request.user_input, client_ip=client_ip
    )

    try:
        allowed, retry_after = check_rate_limit(
            client_ip, settings.rate_limit_per_minute, settings.rate_limit_per_day
        )
    except RedisError as e:
        logger.warning("rate limit check failed, failing open", error=str(e))
        allowed, retry_after = True, 0
    if not allowed:
        logger.warning("rate limit exceeded", client_ip=client_ip)
        raise HTTPException(
            status_code=429,
            detail="Too many requests, please slow down.",
            headers={"Retry-After": str(retry_after)},
        )

    input_hash = hashlib.sha256(request.user_input.strip().lower().encode()).hexdigest()
    cache_key = f"biosignalfoundry:analyze:{input_hash}"
    try:
        cached = redis_client.get(cache_key)
    except RedisError as e:
        logger.warning("cache read failed, treating as cache miss", error=str(e))
        cached = None
    if cached:
        logger.info("cache hit", user_input=request.user_input)

        async def cached_stream():
            yield f"data: {cached}\n\n"

        return StreamingResponse(cached_stream(), media_type="text/event-stream")

    try:
        under_budget = check_and_consume_daily_budget(
            settings.daily_analysis_budget_cap
        )
    except RedisError as e:
        logger.warning("budget check failed, failing open", error=str(e))
        under_budget = True
    if not under_budget:
        logger.warning("daily analysis budget cap reached", client_ip=client_ip)
        raise HTTPException(
            status_code=503,
            detail="Daily analysis volume cap reached, please try again tomorrow.",
        )

    queue: asyncio.Queue = asyncio.Queue()
    callback = StreamingProgressCallback(queue)

    async def run_agent():
        try:
            result = await biosignalfoundry.ainvoke(
                {"messages": [HumanMessage(request.user_input)]},
                config={"callbacks": [callback]},
            )
            structured = result.get("structured_response")
            if isinstance(structured, BioSignalFoundryOutput):
                logger.info("agent final response", agent_response=structured)
                event = {"type": "result", "data": structured.model_dump()}
                try:
                    redis_client.setex(
                        cache_key,
                        REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY,
                        json.dumps(event),
                    )
                except RedisError as e:
                    logger.warning("cache write failed, skipping cache", error=str(e))
                await queue.put(event)
            else:
                logger.error(
                    "agent did not return a structured response",
                    result_keys=list(result.keys()),
                )
                await queue.put(
                    {
                        "type": "error",
                        "message": "Agent did not return a structured response",
                    }
                )
        except Exception as e:
            logger.exception("agent invocation failed", exc_info=e)
            await queue.put({"type": "error", "message": str(e)})
        finally:
            await queue.put(None)

    async def event_stream():
        asyncio.create_task(run_agent())
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("app:app")
