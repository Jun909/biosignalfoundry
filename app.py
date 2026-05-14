import asyncio
import json
from os import getenv
from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.messages import HumanMessage
from pydantic import BaseModel

from config import REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY
from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry
from src.core.logging_config import setup_logging
from src.core.redis_client import redis_client
from src.core.streaming_callback import StreamingProgressCallback

load_dotenv()
logger = setup_logging(
    log_level=getenv("LOG_LEVEL", "INFO"),
    render_json=getenv("ENV") == "production",
)


app = FastAPI()

_raw_origins = getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins: List[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    user_input: str


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    logger.info("analyze request received", user_input=request.user_input)

    cache_key = f"biosignalfoundry:analyze:{request.user_input.strip().lower()}"
    cached = redis_client.get(cache_key)
    if cached:
        logger.info("cache hit", user_input=request.user_input)

        async def cached_stream():
            yield f"data: {cached}\n\n"

        return StreamingResponse(cached_stream(), media_type="text/event-stream")

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
                redis_client.setex(
                    cache_key,
                    REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY,
                    json.dumps(event),
                )
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
