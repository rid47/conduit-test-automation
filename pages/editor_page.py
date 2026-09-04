"""Page object for the article editor (shared by Create and Edit flows --
both live at /editor and /editor/<slug> respectively)."""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.data_generator import ArticleData


class EditorPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title_input = page.locator("input[formcontrolname='title']")
        self.description_input = page.locator("input[formcontrolname='description']")
        self.body_textarea = page.locator("textarea[formcontrolname='body']")
        self.tags_input = page.get_by_placeholder("Enter tags")
        self.publish_button = page.get_by_role("button", name="Publish Article")
        self.error_messages = page.locator(".error-messages li")

    def goto_new(self):
        self.page.goto("/editor")
        expect(self.title_input).to_be_visible()

    def goto_edit(self, slug: str):
        self.page.goto(f"/editor/{slug}")
        expect(self.title_input).to_be_visible()

    def fill_article(self, article: ArticleData):
        self.title_input.fill(article.title)
        self.description_input.fill(article.description)
        self.body_textarea.fill(article.body)
        for tag in article.tags:
            self.tags_input.fill(tag)
            self.tags_input.press("Enter")

    def publish(self):
        self.publish_button.click()
