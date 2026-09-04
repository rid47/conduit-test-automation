"""Page object for a single article view (/article/<slug>)."""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ArticlePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.locator("h1")
        # "Edit Article" / "Delete Article" are rendered twice (meta banner
        # above the body and again below it) -- .first keeps the locator
        # resilient to that duplication instead of failing strict mode.
        self.edit_button = page.get_by_role("link", name="Edit Article").first
        self.delete_button = page.get_by_role("button", name="Delete Article").first
        self.tag_list = page.locator(".tag-list .tag-pill")

    def goto(self, slug: str):
        self.page.goto(f"/article/{slug}")

    def expect_loaded_with_title(self, title: str):
        expect(self.title).to_have_text(title)

    def expect_body_visible(self, body_text: str):
        # The article body renders in a plain, unclassed <p>, so match on
        # its (unique, Faker-generated) text rather than a brittle selector.
        expect(self.page.get_by_text(body_text, exact=False).first).to_be_visible()

    def delete_article(self):
        self.delete_button.click()
