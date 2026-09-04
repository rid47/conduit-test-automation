"""Central runtime configuration, sourced from environment variables (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://conduit.bondaracademy.com")

# Trailing slash matters: Playwright's APIRequestContext resolves relative
# paths against base_url using standard URL-joining rules, so a base_url
# without a trailing slash drops the "/api" segment when a relative path is
# appended (e.g. "articles" -> host/api/articles only if base_url ends in "/").
API_BASE_URL = os.getenv("API_BASE_URL", "https://conduit-api.bondaracademy.com/api/")

# The Conduit Angular app stores its JWT in localStorage under this key and
# expects it back as an `Authorization: Token <jwt>` header on API calls.
AUTH_TOKEN_STORAGE_KEY = "jwtToken"


def build_storage_state(token: str) -> dict:
    """Playwright storage_state seeding the given JWT into localStorage for
    BASE_URL's origin, so a browser context starts already logged in."""
    return {
        "origins": [
            {
                "origin": BASE_URL,
                "localStorage": [{"name": AUTH_TOKEN_STORAGE_KEY, "value": token}],
            }
        ]
    }
