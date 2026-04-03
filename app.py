from os import getenv
from dotenv import load_dotenv
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.messages import HumanMessage
from pydantic import BaseModel

from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry
from src.core.logging_config import setup_logging

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


@app.post("/analyze", response_model=BioSignalFoundryOutput)
async def analyze(request: AnalyzeRequest):
    try:
        logger.info("analyze request received", user_input=request.user_input)
        result = await biosignalfoundry.ainvoke(
            {"messages": [HumanMessage(request.user_input)]}
        )
    except Exception as e:
        logger.exception("agent invocation failed", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

    structured = result.get("structured_response")
    if isinstance(structured, BioSignalFoundryOutput):
        logger.info("agent final response", agent_response=structured)
        return structured

    logger.error(
        "agent did not return a structured response", result_keys=list(result.keys())
    )
    raise HTTPException(
        status_code=500, detail="Agent did not return a structured response"
    )


if __name__ == "__main__":
    uvicorn.run("app:app")
