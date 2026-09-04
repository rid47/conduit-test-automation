"""Edit Article scenario (article created via API as a pre-condition)."""
import re

import allure
from playwright.sync_api import Page, expect

from api.api_client import ApiClient
from config.settings import BASE_URL, build_storage_state
from pages.article_page import ArticlePage
from pages.editor_page import EditorPage
from utils.data_generator import random_article, random_user


@allure.epic("Conduit")
@allure.feature("Edit Article")
class TestEditArticle:
    @allure.title("Editing an article's title/body via the UI persists the change")
    def test_edit_article_success(self, page: Page, api_client: ApiClient, registered_user: dict):
        with allure.step("Create the precondition article via the API"):
            original = random_article()
            created = api_client.create_article(registered_user["token"], original)

        editor = EditorPage(page)
        updated = random_article()

        with allure.step("Open the article for editing and confirm it's pre-filled with the original data"):
            editor.goto_edit(created["slug"])
            expect(editor.title_input).to_have_value(original.title)
            expect(editor.body_textarea).to_have_value(original.body)

        with allure.step("Replace the title/description/body and republish"):
            editor.title_input.fill(updated.title)
            editor.description_input.fill(updated.description)
            editor.body_textarea.fill(updated.body)
            editor.publish()

        with allure.step("The article page reflects the updated content"):
            expect(page).to_have_url(re.compile(r"/article/"))
            article_page = ArticlePage(page)
            article_page.expect_loaded_with_title(updated.title)
            article_page.expect_body_visible(updated.body)

        with allure.step("The update survives a reload (data persistence)"):
            page.reload()
            article_page.expect_loaded_with_title(updated.title)
            article_page.expect_body_visible(updated.body)

    @allure.title("A user cannot edit another user's article")
    def test_edit_article_by_non_owner_is_blocked(self, page: Page, api_client: ApiClient, registered_user: dict):
        with allure.step("Create the precondition article via the API, owned by the primary session user"):
            original = random_article()
            created = api_client.create_article(registered_user["token"], original)

        with allure.step("Register a second, unrelated user via the API"):
            other_user = api_client.register_user(random_user())

        with allure.step("As the second user, the article page shows no Edit/Delete controls"):
            other_context = page.context.browser.new_context(
                base_url=BASE_URL, storage_state=build_storage_state(other_user["token"])
            )
            other_page = other_context.new_page()
            other_article_page = ArticlePage(other_page)
            other_article_page.goto(created["slug"])
            expect(other_article_page.edit_button).not_to_be_visible()
            expect(other_article_page.delete_button).not_to_be_visible()

        with allure.step("Directly navigating to the edit URL for someone else's article redirects away, not to the editor"):
            other_page.goto(f"/editor/{created['slug']}")
            expect(other_page).not_to_have_url(re.compile(r"/editor/"))
            other_context.close()

        with allure.step("The original article remains unchanged"):
            article_page = ArticlePage(page)
            article_page.goto(created["slug"])
            article_page.expect_loaded_with_title(original.title)
