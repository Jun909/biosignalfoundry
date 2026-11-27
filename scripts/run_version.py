"""
Run one registered version of the agent on one or more tickers and print the result.

For trying a version by hand. Unlike ``record_signal.py`` this does NOT touch Postgres:
it does not register the version in ``system_versions``, fetch entry prices or store a
trade. The data providers still use Redis for their response caches, and the LLM and
data APIs are called for real (this costs LLM tokens and API calls).

The version is built exactly as paper trading builds it (``build_agent``): its prompts and
tool interfaces are checked against the pinned hashes, and it runs on the LLM the version
pins. Pass --use-default-llm to run on the LLM chosen by ``LLM_PROVIDER`` instead.

Usage:
    uv run python scripts/run_version.py --version v2.0.0 --ticker ALDX
    uv run python scripts/run_version.py --version v2.0.0 --ticker ALDX,MRNA,GILD
    uv run python scripts/run_version.py --ticker ALDX --use-default-llm
    uv run python scripts/run_version.py --version v2.0.0 --ticker ALDX --trace
    uv run python scripts/run_version.py --version v2.0.0 --ticker ALDX --json
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage

from config import settings
from src.core.logging_config import setup_logging
from src.core.subagent_capture import capture_subagent_outputs
from src.core.version_registry import (DEFAULT_VERSION, VERSIONS, VersionError,
                                       get_version)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a registered version on tickers, without writing to the database"
    )
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help=f"Registered version label (default: {DEFAULT_VERSION}; "
        f"available: {', '.join(VERSIONS)})",
    )
    parser.add_argument(
        "--ticker",
        required=True,
        help="Ticker, or comma-separated tickers run one after another",
    )
    parser.add_argument(
        "--use-default-llm",
        action="store_true",
        help="Run on the LLM from LLM_PROVIDER instead of the one the version pins",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Also print the supervisor's message history (tool calls and results)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print one JSON object per ticker instead of the readable report",
    )
    return parser.parse_args()


def _content_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return json.dumps(content, default=str)


def _print_trace(messages) -> None:
    print("\n--- supervisor message trace ---")
    for message in messages:
        kind = type(message).__name__
        for call in getattr(message, "tool_calls", None) or []:
            args = json.dumps(call.get("args"), default=str)
            print(f"[{kind}] tool_call {call.get('name')}: {args[:400]}")
        text = _content_text(message).strip()
        if text:
            print(f"[{kind}] {text[:1500]}")


async def _run_ticker(agent, ticker: str) -> dict:
    started = time.monotonic()
    with capture_subagent_outputs() as subagents:
        result = await agent.ainvoke({"messages": [HumanMessage(f"Analyze {ticker}")]})
    decision = result.get("structured_response")
    return {
        "ticker": ticker,
        "seconds": round(time.monotonic() - started, 1),
        "decision": decision.model_dump(mode="json") if decision else None,
        "subagents": subagents,
        "messages": result.get("messages", []),
    }


def _print_report(label: str, run: dict, trace: bool) -> None:
    print(f"\n{'=' * 70}\n{label}  {run['ticker']}  ({run['seconds']}s)\n{'=' * 70}")
    for sub in run["subagents"]:
        print(f"\n--- {sub['subagent']} ---")
        print(json.dumps(sub["output"], indent=2, default=str))
    decision = run["decision"]
    print("\n--- supervisor decision ---")
    if decision:
        print(
            f"{decision['decision'].upper()}  confidence={decision['confidence']}\n"
            f"{decision['reasoning']}"
        )
    else:
        print("No structured response returned.")
    if trace:
        _print_trace(run["messages"])


async def main() -> int:
    args = _parse_args()
    setup_logging(log_level=settings.log_level, render_json=False)

    try:
        config = get_version(args.version)
    except VersionError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    # Imported here: importing it builds the default agent and LLM (needs LLM_PROVIDER).
    from src.biosignalfoundry import build_agent

    try:
        if args.use_default_llm:
            from llm_provider import llm

            agent = build_agent(args.version, model=llm)
        else:
            agent = build_agent(args.version)
    except VersionError as e:  # VersionDrift (edited prompt/tools) or missing builder
        print(f"error: {e}", file=sys.stderr)
        return 2

    llm_desc = (
        f"default LLM ({settings.llm_provider})"
        if args.use_default_llm
        else f"{config.llm.provider}/{config.llm.model} T={config.llm.temperature}"
    )
    print(f"{args.version}: {config.description}")
    print(f"subagents: {', '.join(config.subagents)} | llm: {llm_desc}")

    failed = 0
    for ticker in [t.strip().upper() for t in args.ticker.split(",") if t.strip()]:
        try:
            run = await _run_ticker(agent, ticker)
        except Exception as e:
            failed += 1
            print(f"\n{ticker}: FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        if run["decision"] is None:
            failed += 1
        if args.json:
            payload = {k: v for k, v in run.items() if k != "messages"}
            payload["version"] = args.version
            print(json.dumps(payload, default=str))
        else:
            _print_report(args.version, run, args.trace)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
