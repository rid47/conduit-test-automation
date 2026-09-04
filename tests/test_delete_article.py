"""Delete Article scenario (article created via API as a pre-condition)."""
import re

import allure
from playwright.sync_api import Page, expect

from api.api_client import ApiClient
from pages.article_page import ArticlePage
from pages.home_page import HomePage
from utils.data_generator import random_article


@allure.epic("Conduit")
@allure.feature("Delete Article")
class TestDeleteArticle:
    @allure.title("Deleting an article redirects home and removes it from the feed")
    def test_delete_article_success(self, page: Page, api_client: ApiClient, registered_user: dict):
        with allure.step("Create the precondition article via the API"):
            article = random_article()
            created = api_client.create_article(registered_user["token"], article)

        article_page = ArticlePage(page)

        with allure.step("Open the article and delete it"):
            article_page.goto(created["slug"])
            article_page.expect_loaded_with_title(article.title)
            article_page.delete_article()

        with allure.step("The app redirects to the home page"):
            expect(page).to_have_url(re.compile(r"^https?://[^/]+/?$"))

        with allure.step("The deleted article is gone from the global feed"):
            home = HomePage(page)
            home.goto()
            home.click_global_feed()
            assert article.title not in home.article_preview_titles(), "Deleted article still appears in the feed"

        with allure.step("Revisiting the deleted article's URL no longer shows its content"):
            article_page.goto(created["slug"])
            expect(article_page.delete_button).not_to_be_visible()

    @allure.title("Visiting a non-existent article slug does not render article content or delete controls")
    def test_delete_nonexistent_article_is_handled_gracefully(self, page: Page):
        article_page = ArticlePage(page)

        with allure.step("Navigate directly to a slug that was never created"):
            article_page.goto("this-slug-has-never-existed-0000000")

        with allure.step("No delete/edit controls are rendered for a non-existent article"):
            expect(article_page.delete_button).not_to_be_visible()
            expect(article_page.edit_button).not_to_be_visible()
