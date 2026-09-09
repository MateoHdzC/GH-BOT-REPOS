
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Dict, Optional, Tuple

import keyring
from src.utils.logger import log_event

SERVICE_NAME = "GH-BOT-REPOS-WINDOWS"
CREDENTIAL_KEY = "github_pat"
USER_KEY = "github_username"

class GitHubCredentials:

    @staticmethod
    def store_token(token: str, username: str = "") -> bool:
        clean_token = token.strip()
        if not clean_token:
            return False
        try:
            keyring.set_password(SERVICE_NAME, CREDENTIAL_KEY, clean_token)
            if username:
                keyring.set_password(SERVICE_NAME, USER_KEY, username)
            log_event("SYSTEM", "GitHub credentials securely stored in Windows Credential Manager")
            return True
        except Exception as ex:
            log_event("ERROR", f"Failed to store credential in Windows Credential Manager: {ex}")
            return False

    @staticmethod
    def get_token() -> Optional[str]:
        try:
            return keyring.get_password(SERVICE_NAME, CREDENTIAL_KEY)
        except Exception as ex:
            log_event("ERROR", f"Failed to retrieve credential: {ex}")
            return None

    @staticmethod
    def get_username() -> Optional[str]:
        try:
            return keyring.get_password(SERVICE_NAME, USER_KEY)
        except Exception:
            return None

    @staticmethod
    def delete_token() -> bool:
        try:
            keyring.delete_password(SERVICE_NAME, CREDENTIAL_KEY)
            try:
                keyring.delete_password(SERVICE_NAME, USER_KEY)
            except Exception:
                pass
            log_event("SYSTEM", "GitHub credentials removed from Windows Credential Manager")
            return True
        except Exception as ex:
            log_event("ERROR", f"Failed to delete credential: {ex}")
            return False

    @classmethod
    def validate_token(cls, token: Optional[str] = None) -> Tuple[bool, Dict[str, str], str]:
        tok = cls.get_token() if token is None else token.strip()
        if not tok:
            return False, {}, "No token configured"

        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {tok}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GH-BOT-REPOS-Windows/1.0",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    user_info = {
                        "login": data.get("login", ""),
                        "name": data.get("name", "") or data.get("login", ""),
                        "html_url": data.get("html_url", ""),
                    }
                    return True, user_info, ""
                return False, {}, f"GitHub returned HTTP {response.status}"
        except urllib.error.HTTPError as ex:
            if ex.code == 401:
                return False, {}, "Token invalid or expired (401 Unauthorized)"
            if ex.code == 403:
                return False, {}, "Rate limit exceeded or insufficient scope (403)"
            return False, {}, f"GitHub HTTP error: {ex.code}"
        except urllib.error.URLError as ex:
            return False, {}, f"Network connection failed: {ex.reason}"
        except Exception as ex:
            return False, {}, f"Validation error: {ex}"
