"""Unit tests for GitHub credentials manager."""

from unittest.mock import patch
from src.git.credentials import GitHubCredentials


def test_github_credentials_store_and_get():
    with patch("keyring.set_password") as mock_set, patch("keyring.get_password") as mock_get:
        mock_get.return_value = "ghp_fake_token_for_testing"

        success = GitHubCredentials.store_token("ghp_fake_token_for_testing", "testuser")
        assert success is True
        mock_set.assert_called()

        retrieved = GitHubCredentials.get_token()
        assert retrieved == "ghp_fake_token_for_testing"


def test_github_credentials_delete():
    with patch("keyring.delete_password") as mock_del:
        success = GitHubCredentials.delete_token()
        assert success is True
        mock_del.assert_called()


def test_github_credentials_validate_empty():
    valid, user_info, err = GitHubCredentials.validate_token("")
    assert valid is False
    assert "No token" in err
