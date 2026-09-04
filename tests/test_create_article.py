"""Create New Article scenario."""
import re

import allure
from playwright.sync_api import Page, expect

from pages.article_page import ArticlePage
from pages.editor_page import EditorPage
from pages.home_page import HomePage
from utils.data_generator import random_article


@allure.epic("Conduit")
@allure.feature("Create Article")
class TestCreateArticle:
    @allure.title("Publishing an article with valid data redirects to the new article and persists it")
    def test_create_article_success(self, page: Page):
        editor = EditorPage(page)
        article = random_article()

        with allure.step("Fill and publish a new article with randomized data"):
            editor.goto_new()
            editor.fill_article(article)
            editor.publish()

        with allure.step("The new article page loads with the submitted title, body and tags"):
            expect(page).to_have_url(re.compile(r"/article/"))
            article_page = ArticlePage(page)
            article_page.expect_loaded_with_title(article.title)
            article_page.expect_body_visible(article.body)
            for tag in article.tags:
                expect(article_page.tag_list.filter(has_text=tag)).to_have_count(1)

        with allure.step("The article shows up in the global feed (data persistence)"):
            home = HomePage(page)
            home.goto()
            home.click_global_feed()
            expect(home.article_previews.first).to_be_visible()
            assert article.title in home.article_preview_titles(), "New article not found in the global feed"

    @allure.title("Publishing an article without a title is rejected with a validation error")
    def test_create_article_missing_title_shows_error(self, page: Page):
        editor = EditorPage(page)
        article = random_article()

        with allure.step("Submit the editor with the title left blank"):
            editor.goto_new()
            editor.description_input.fill(article.description)
            editor.body_textarea.fill(article.body)
            editor.publish()

        with allure.step("A 'title can't be blank' validation error is shown and no article is created"):
            expect(editor.error_messages).to_contain_text("title can't be blank")
            expect(page).to_have_url(re.compile(r"/editor$"))
