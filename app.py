import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from src.biothrone import BiothroneOutput, biothrone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    user_input: str


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = biothrone.invoke(
        {"messages": [HumanMessage(request.user_input)]},
    )

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            parsed = msg.additional_kwargs.get("parsed")
            if parsed and isinstance(parsed, BiothroneOutput):
                return {
                    "ticker": parsed.ticker,
                    "decision": parsed.decision,
                    "confidence": parsed.confidence,
                    "reasoning": parsed.reasoning,
                }

    raise HTTPException(
        status_code=500,
        detail="Could not parse structured output from agent",
    )


if __name__ == "__main__":
    uvicorn.run("app:app")
