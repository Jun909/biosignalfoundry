import asyncio

from langchain_core.callbacks import AsyncCallbackHandler

TOOL_LABELS: dict[str, str] = {
    "get_company_profile": "Fetching company profile",
    "get_income_statement_annual": "Fetching annual income statement",
    "financial_health_agent": "Running financial health analysis",
}


class StreamingProgressCallback(AsyncCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        name = serialized.get("name", "")  # serialized returns the name of the tool
        label = TOOL_LABELS.get(name, f"Running {name}...")
        await self.queue.put({"type": "progress", "message": label})
