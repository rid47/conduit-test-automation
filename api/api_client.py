"""Thin wrapper over Playwright's APIRequestContext for the Conduit REST API.

Used to satisfy the "create the article via API as a pre-condition" note in
the assignment, and to register throwaway users without going through the UI
signup flow (faster, and keeps the session-reuse fixture simple).
"""
from playwright.sync_api import APIRequestContext

from utils.data_generator import ArticleData, UserData


class ApiClient:
    def __init__(self, request_context: APIRequestContext):
        self._request = request_context

    def register_user(self, user: UserData) -> dict:
        """POST /api/users -> {"user": {..., "token": "<jwt>"}}"""
        response = self._request.post(
            "users",
            data={"user": {"username": user.username, "email": user.email, "password": user.password}},
        )
        assert response.ok, f"User registration failed: {response.status} {response.text()}"
        return response.json()["user"]

    def get_current_user(self, token: str) -> dict:
        """GET /api/user -> {"user": {...}} for the token's owner."""
        response = self._request.get("user", headers={"Authorization": f"Token {token}"})
        assert response.ok, f"Fetching current user failed: {response.status} {response.text()}"
        return response.json()["user"]

    def create_article(self, token: str, article: ArticleData) -> dict:
        """POST /api/articles -> {"article": {..., "slug": "..."}}

        The Conduit API generates the slug server-side (title + timestamp +
        id), so callers must read it back from the response rather than
        deriving it from the title themselves.
        """
        response = self._request.post(
            "articles",
            data={
                "article": {
                    "title": article.title,
                    "description": article.description,
                    "body": article.body,
                    "tagList": article.tags,
                }
            },
            headers={"Authorization": f"Token {token}"},
        )
        assert response.ok, f"Article creation failed: {response.status} {response.text()}"
        return response.json()["article"]
