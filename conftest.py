"""Root fixtures: one authenticated user per pytest-xdist worker, registered
via the API and reused across every test in that worker's session (see the
"Session Management" requirement) via Playwright's storage_state mechanism.
"""
import pytest
from playwright.sync_api import Playwright

from api.api_client import ApiClient
from config.settings import API_BASE_URL, BASE_URL, build_storage_state
from utils.data_generator import UserData, random_user


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright):
    context = playwright.request.new_context(base_url=API_BASE_URL)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def api_client(api_request_context) -> ApiClient:
    return ApiClient(api_request_context)


@pytest.fixture(scope="session")
def registered_user(api_client: ApiClient) -> dict:
    """One throwaway, randomly-generated user per worker process -- created
    once via the API and reused for every test that process runs."""
    user: UserData = random_user()
    api_user = api_client.register_user(user)
    return {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "token": api_user["token"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, registered_user):
    """Seeds every browser context with the registered user's JWT via
    storage_state, so tests start already authenticated -- no UI login,
    and no repeated logins between tests."""
    storage_state = build_storage_state(registered_user["token"])
    return {**browser_context_args, "base_url": BASE_URL, "storage_state": storage_state}
