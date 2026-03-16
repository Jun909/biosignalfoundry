import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from src.biothrone import biothrone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    user_input: str


def stream_biothrone(user_input: str):
    for namespace, chunk in biothrone.stream(
        {"messages": [HumanMessage(user_input)]},
        stream_mode="messages",
        subgraphs=True,
    ):
        token, metadata = chunk

        # Only main agent (empty namespace), ignore all subagent traffic
        if namespace:
            continue

        # if we use response_format
        # for node_name, data in chunk.items():
        #     messages = data.get("messages", [])
        #     if not messages:
        #         continue

        #     last_msg = messages[-1]

        #     # The final structured response is an AIMessage with no tool calls
        #     if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
        #         output = last_msg.additional_kwargs.get("parsed")
        #         if output and isinstance(output, BiothroneOutput):
        #             print(f"Ticker:     {output.ticker}")
        #             print(f"Decision:   {output.decision}")
        #             print(f"Confidence: {output.confidence}")
        #             print(f"Reasoning:  {output.reasoning}")

        # Only AI-generated text tokens, skip tool calls and tool results
        if not isinstance(token, AIMessage):
            continue
        if token.tool_call_chunks:
            continue

        # Stream the final response token by token
        if token.content:
            yield f"data: {token.content}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    return StreamingResponse(
        stream_biothrone(request.user_input),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    uvicorn.run("app:app")
