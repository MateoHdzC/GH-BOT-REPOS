"""Unit tests for utility functions and token sanitization."""

from src.utils.logger import sanitize_message


def test_sanitize_message_ghp_token():
    raw = "Push error: authentication failed for https://ghp_abcdef12345678901234567890123456@github.com"
    clean = sanitize_message(raw)
    assert "ghp_abcdef" not in clean
    assert "[REDACTED_SECRET]" in clean


def test_sanitize_message_github_pat():
    raw = "Using token github_pat_11AAAAAAA00000000000000000000000000000000000000000000000000000000000000000 to authenticate"
    clean = sanitize_message(raw)
    assert "github_pat_" not in clean
    assert "[REDACTED_SECRET]" in clean


def test_sanitize_message_bearer():
    raw = "Header Authorization: Bearer secret_access_token_1234567890_abc"
    clean = sanitize_message(raw)
    assert "secret_access_token" not in clean
    assert "[REDACTED_SECRET]" in clean
