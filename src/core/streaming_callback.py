import asyncio

from langchain_core.callbacks import AsyncCallbackHandler

TOOL_LABELS: dict[str, str] = {
    "get_company_profile": "Fetching company profile",
    "get_income_statement_annual": "Fetching annual income statement",
    "financial_health_agent": "Running financial health analysis",
    "get_fda_approvals": "Fetching FDA approval history",
    "get_fda_complete_response_letters": "Fetching FDA complete response letters",
    "get_recent_8k_events": "Fetching recent SEC 8-K events",
    "clinical_pipeline_agent": "Running clinical pipeline analysis",
}


class StreamingProgressCallback(AsyncCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        name = serialized.get("name", "")  # serialized returns the name of the tool
        label = TOOL_LABELS.get(name, f"Running {name}...")
        await self.queue.put({"type": "progress", "message": label})
