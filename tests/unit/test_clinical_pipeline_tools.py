"""
Tests for src/agent_tools/clinical_pipeline_agent_tools.py.

Pure _process_* / helper tests need no mocking. The tool-level tests mock the module
singletons (finnclient, fdaclient, the SEC client) so no HTTP calls are made.
"""

from unittest.mock import MagicMock, patch

import pytest

import src.agent_tools.clinical_pipeline_agent_tools as tools_module
from src.agent_tools.clinical_pipeline_agent_tools import (
    _letter_excerpt, _process_8k, _process_crl, _process_fda_approvals,
    _summarize_application, get_fda_approvals,
    get_fda_complete_response_letters, get_recent_8k_events)

APPLICATION = {
    "application_number": "NDA219209",
    "sponsor_name": "VERTEX PHARMS INC",
    "products": [
        {
            "brand_name": "JOURNAVX",
            "marketing_status": "Prescription",
            "active_ingredients": [{"name": "SUZETRIGINE", "strength": "50MG"}],
        }
    ],
    "submissions": [
        {
            "submission_type": "SUPPL",
            "submission_status": "AP",
            "submission_status_date": "20260123",
            "submission_class_code_description": "Labeling",
        },
        {
            "submission_type": "ORIG",
            "submission_status": "AP",
            "submission_status_date": "20250130",
            "review_priority": "PRIORITY",
        },
    ],
}


def test_application_summary_picks_original_approval_and_latest_submission():
    out = _summarize_application(APPLICATION)

    assert out["brand_names"] == ["JOURNAVX"]
    assert out["active_ingredients"] == ["SUZETRIGINE"]
    assert out["original_approval_date"] == "2025-01-30"
    assert out["review_priority"] == "PRIORITY"
    assert out["supplements"] == 1
    assert out["latest_submission"]["date"] == "2026-01-23"
    assert out["latest_submission"]["class"] == "Labeling"


def test_approvals_are_sorted_newest_first_and_capped():
    apps = []
    for i in range(20):
        app = {**APPLICATION, "application_number": f"NDA{i}"}
        app["submissions"] = [
            {
                "submission_type": "ORIG",
                "submission_status": "AP",
                "submission_status_date": f"20{i:02d}0101",
            }
        ]
        apps.append(app)

    out = _process_fda_approvals("VRTX", "Vertex", apps, truncated=False)

    assert out["application_count"] == 20
    assert len(out["applications"]) == tools_module.MAX_APPLICATIONS
    assert out["applications_omitted"] == 5
    assert out["applications"][0]["application_number"] == "NDA19"


def test_empty_approvals_carry_the_biologics_caveat():
    out = _process_fda_approvals("MRNA", "Moderna, Inc.", [], truncated=False)

    assert out["ok"] is True
    assert out["applications"] == []
    assert "biologics" in out["note"].lower()
    assert "No NDA/ANDA applications" in out["message"]


def test_truncated_provider_result_is_flagged():
    out = _process_fda_approvals("X", "X", [APPLICATION], truncated=True)
    assert "truncated" in out["warning"]


def test_letter_excerpt_starts_at_the_decision_sentence():
    text = (
        "U.S. FOOD & DRUG ADMINISTRATION Lg YN U.S.   Dear Sir: Please refer to your "
        "new drug application. We have completed our review of this application and "
        "have determined that we cannot approve this application in its present form. "
        + "reasons " * 200
    )
    out = _letter_excerpt(text)

    assert out.startswith("We have completed our review")
    assert len(out) <= tools_module.LETTER_EXCERPT_CHARS + 3
    assert out.endswith("...")


def test_letter_excerpt_handles_missing_text():
    assert _letter_excerpt(None) == ""


def test_crl_letters_sorted_by_real_date_and_status_kept():
    letters = [
        {"letter_date": "12/01/2024", "approval_status": "Approved", "text": "a"},
        {"letter_date": "03/16/2026", "approval_status": "Unapproved", "text": "b"},
        {"letter_date": "04/02/2025", "approval_status": "Unapproved", "text": "c"},
    ]
    out = _process_crl("ALDX", "Aldeyra", letters)

    assert [x["letter_date"] for x in out["letters"]] == [
        "03/16/2026",
        "04/02/2025",
        "12/01/2024",
    ]
    assert out["letters"][0]["approval_status"] == "Unapproved"
    assert "published" in out["note"]


def test_crl_none_found():
    out = _process_crl("MRNA", "Moderna", [])
    assert out["letter_count"] == 0
    assert "No published complete response letters" in out["message"]


def _filing(date, items, press_release=None, details=None):
    return {
        "filing_date": f"{date}T00:00:00+00:00",
        "items_reported": items,
        "press_release": press_release,
        "details": details or [],
        "url": f"https://sec.gov/{date}",
    }


def test_8k_keeps_relevant_items_and_drops_noise_filings():
    filings = [
        _filing("2026-11-13", ["5.02", "9.01"]),
        _filing(
            "2026-11-09",
            ["8.01"],
            details=[
                {
                    "item_id": "8.01",
                    "display_name": "Other Events",
                    "title": "Other Events",
                    "content": "Company asked the FDA for a review.",
                }
            ],
        ),
    ]
    out = _process_8k("ALDX", filings)

    assert out["filings_scanned"] == 2
    assert out["event_count"] == 1
    event = out["events"][0]
    assert event["filing_date"] == "2026-11-09"
    assert event["text_excerpt"] == "Company asked the FDA for a review."


def test_8k_prefers_press_release_over_boilerplate_item_text():
    details = [
        {
            "item_id": "7.01",
            "display_name": "Regulation FD",
            "title": "t",
            "content": "furnished press release",
        }
    ]
    out = _process_8k(
        "X",
        [
            _filing(
                "2026-01-01",
                ["7.01"],
                press_release="Big trial result " * 300,
                details=details,
            )
        ],
    )

    event = out["events"][0]
    assert "text_excerpt" not in event
    assert (
        len(event["press_release_excerpt"])
        <= tools_module.PRESS_RELEASE_EXCERPT_CHARS + 3
    )


def test_8k_caps_event_count_and_explains_empty_results():
    many = [
        _filing(f"2026-01-{i:02d}", ["8.01"], press_release="x" * 50)
        for i in range(1, 20)
    ]
    assert len(_process_8k("X", many)["events"]) == tools_module.MAX_8K_FILINGS

    assert "Foreign private issuers" in _process_8k("ASND", [])["message"]
    assert (
        "None of the recent 8-Ks"
        in _process_8k("X", [_filing("2026-01-01", ["5.02"])])["message"]
    )


# ---------------------------------------------------------------------------
# Tool-level wiring
# ---------------------------------------------------------------------------


@pytest.fixture
def profile():
    with patch.object(
        tools_module.finnclient,
        "company_profile2",
        return_value={"ok": True, "data": {"name": "Intra-Cellular Therapies Inc"}},
    ) as m:
        yield m


def _fda_response(results, truncated=False):
    return {"ok": True, "data": {"results": results}, "truncated": truncated}


def test_approvals_tool_falls_back_to_second_search_key_and_filters_sponsors(profile):
    first = _fda_response([])
    second = _fda_response(
        [
            {**APPLICATION, "sponsor_name": "INTRA-CELLULAR"},
            {**APPLICATION, "application_number": "NDA1", "sponsor_name": "INTRABIO"},
        ]
    )
    with patch.object(
        tools_module.fdaclient, "query_all", side_effect=[first, second]
    ) as q:
        out = get_fda_approvals.invoke({"ticker": " itci "})

    assert out["ok"] is True
    assert out["ticker"] == "ITCI"
    assert out["matched_sponsors"] == ["INTRA-CELLULAR"]
    assert out["application_count"] == 1
    assert q.call_count == 2


def test_approvals_tool_returns_do_not_retry_on_provider_error(profile):
    with patch.object(
        tools_module.fdaclient,
        "query_all",
        return_value={"ok": False, "error": "500 Server Error"},
    ):
        out = get_fda_approvals.invoke({"ticker": "ITCI"})

    assert out["ok"] is False
    assert "Do not retry" in out["instruction"]


def test_tools_report_missing_company_profile():
    with patch.object(
        tools_module.finnclient,
        "company_profile2",
        return_value={"ok": True, "data": {}},
    ):
        a = get_fda_approvals.invoke({"ticker": "ZZZZ"})
        b = get_fda_complete_response_letters.invoke({"ticker": "ZZZZ"})

    for out in (a, b):
        assert out["ok"] is False
        assert "No company profile" in out["error"]


def test_crl_tool_filters_to_matching_company(profile):
    letters = [
        {
            "company_name": "Intra-Cellular Therapies, Inc.",
            "letter_date": "01/02/2025",
            "text": "x",
        },
        {"company_name": "Intrabio Ltd", "letter_date": "01/02/2024", "text": "y"},
    ]
    with patch.object(
        tools_module.fdaclient, "query_all", return_value=_fda_response(letters)
    ):
        out = get_fda_complete_response_letters.invoke({"ticker": "ITCI"})

    assert out["letter_count"] == 1
    assert out["letters"][0]["company_name"] == "Intra-Cellular Therapies, Inc."


def test_8k_tool_uses_sec_client_and_reports_failure_without_retry_hint_loss():
    sec = MagicMock()
    sec.get_8k_data.return_value = {
        "ok": True,
        "data": [_filing("2026-11-09", ["8.01"], press_release="FDA update")],
    }
    with patch.object(tools_module, "_sec_client", return_value=sec):
        out = get_recent_8k_events.invoke({"ticker": "aldx"})
    sec.get_8k_data.assert_called_once_with("ALDX", limit=tools_module.FILINGS_TO_SCAN)
    assert out["event_count"] == 1

    sec.get_8k_data.return_value = {"ok": False, "error": "Company not found"}
    with patch.object(tools_module, "_sec_client", return_value=sec):
        out = get_recent_8k_events.invoke({"ticker": "ITCI"})
    assert out["ok"] is False
    assert "Do not retry" in out["instruction"]


def test_8k_tool_handles_missing_sec_identity():
    with patch.object(
        tools_module,
        "_sec_client",
        side_effect=RuntimeError("SEC_EDGAR_IDENTITY is not set"),
    ):
        out = get_recent_8k_events.invoke({"ticker": "MRNA"})

    assert out["ok"] is False
    assert "SEC_EDGAR_IDENTITY" in out["error"]
