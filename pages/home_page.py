"""Page object for the home/feed page, including the tag-filter sidebar."""
import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.tag_pills = page.locator(".tag-list a.tag-pill")
        self.feed_tabs = page.locator(".feed-toggle .nav-link")
        # .first: an unrelated icon element inside .feed-toggle can also
        # briefly carry .nav-link.active, so pin to the actual tab (always
        # first in DOM order).
        self.active_feed_tab = page.locator(".feed-toggle .nav-link.active").first
        self.article_previews = page.locator(".article-preview")
        self.empty_state_message = page.get_by_text("No articles are here... yet.")

    def goto(self):
        self.page.goto("/")

    def click_tag(self, tag_name: str):
        # Tag pills are plain <a> elements without an href (SPA click
        # handler only), so they carry no accessible "link" role -- match by
        # exact (whitespace-trimmed) text instead of using get_by_role, and
        # anchor the regex so "Git" doesn't also match "GitHub".
        self.tag_pills.filter(has_text=re.compile(rf"^\s*{re.escape(tag_name)}\s*$")).first.click()

    def click_global_feed(self):
        # "Your Feed" (followed authors only) is the default active tab for
        # an authenticated user, so a just-created article -- which the
        # session user always "owns" but never follows -- only shows up
        # once "Global Feed" is selected explicitly.
        self.feed_tabs.filter(has_text=re.compile(r"^\s*Global Feed\s*$")).click()
        expect(self.active_feed_tab).to_have_text("Global Feed")

    def expect_active_tab(self, tag_name: str):
        expect(self.active_feed_tab).to_have_text(tag_name)

    def article_preview_titles(self) -> list[str]:
        # The empty-state placeholder shares the .article-preview class, and
        # this immediate snapshot has no auto-retry, so wait for a real
        # article link to attach first -- otherwise a feed re-render still
        # in flight (e.g. right after switching tabs) can be read as empty.
        preview_links = self.article_previews.locator("a.preview-link h1")
        expect(preview_links.first).to_be_attached()
        return preview_links.all_text_contents()

    def article_preview_tags(self, index: int) -> list[str]:
        # Wait for this preview's tag pills to actually render before
        # snapshotting -- all_text_contents() takes an instant read with no
        # auto-retry, so calling it right after a feed re-render can race
        # ahead of Angular finishing the DOM update.
        tag_locator = self.article_previews.nth(index).locator(".tag-list li")
        expect(tag_locator.first).to_be_attached()
        return tag_locator.all_text_contents()
