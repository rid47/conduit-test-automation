"""Page object for a user's public profile (/profile/<username>).

Used to verify Settings updates actually persisted: the Settings page
itself has a known app bug where its form never re-populates on load (see
README), so the public profile page is the reliable, user-visible surface
to confirm bio/image changes really saved.
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.avatar = page.locator("img.user-img")

    def goto(self, username: str):
        self.page.goto(f"/profile/{username}")

    def expect_bio_visible(self, bio_text: str):
        expect(self.page.get_by_text(bio_text, exact=False).first).to_be_visible()
