import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.messages import HumanMessage
from pydantic import BaseModel

from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    user_input: str


@app.post("/analyze", response_model=BioSignalFoundryOutput)
async def analyze(request: AnalyzeRequest):
    try:
        result = await biosignalfoundry.ainvoke({"messages": [HumanMessage(request.user_input)]})
    except Exception as e:
        logger.exception("Agent invocation failed")
        raise HTTPException(status_code=500, detail=str(e))

    structured = result.get("structured_response")
    if isinstance(structured, BioSignalFoundryOutput):
        return structured

    logger.error("No structured_response in result. Keys: %s", list(result.keys()))
    raise HTTPException(status_code=500, detail="Agent did not return a structured response")


if __name__ == "__main__":
    uvicorn.run("app:app")
