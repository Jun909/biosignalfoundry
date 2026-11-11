import re
import subprocess
from unittest.mock import patch

from src.core import versioning


def test_prompt_hash_is_stable_and_order_independent():
    a = {"x": "hello", "y": "world"}
    b = {"y": "world", "x": "hello"}
    assert versioning.prompt_hash(a) == versioning.prompt_hash(b)
    assert len(versioning.prompt_hash(a)) == 8


def test_prompt_hash_ignores_whitespace_churn():
    base = {"x": "line one\nline two"}
    churned = {"x": "line one  \r\nline two\n\n"}
    assert versioning.prompt_hash(base) == versioning.prompt_hash(churned)


def test_prompt_hash_changes_when_text_changes():
    assert versioning.prompt_hash({"x": "buy"}) != versioning.prompt_hash({"x": "sell"})


def test_prompt_hash_changes_when_prompt_is_renamed():
    assert versioning.prompt_hash({"x": "same"}) != versioning.prompt_hash(
        {"y": "same"}
    )


def test_git_sha_prefers_env_var(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abcdef1234567")
    assert versioning.git_sha() == "abcdef1"


def test_git_sha_falls_back_to_nogit(monkeypatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    with patch.object(versioning.subprocess, "run", side_effect=OSError):
        assert versioning.git_sha() == "nogit"
        assert versioning.is_dirty() is False


def test_git_failure_is_swallowed(monkeypatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    err = subprocess.CalledProcessError(128, "git")
    with patch.object(versioning.subprocess, "run", side_effect=err):
        assert versioning.git_sha() == "nogit"


def test_system_version_format_and_dirty_suffix():
    with (
        patch.object(versioning, "git_sha", return_value="abc1234"),
        patch.object(versioning, "is_dirty", return_value=False),
    ):
        clean = versioning.system_version()
    assert re.fullmatch(r"abc1234-[0-9a-f]{8}", clean)

    with (
        patch.object(versioning, "git_sha", return_value="abc1234"),
        patch.object(versioning, "is_dirty", return_value=True),
    ):
        assert versioning.system_version() == f"{clean}-dirty"
    assert len(clean) + len("-dirty") <= 32  # fits paper_trades.system_version
