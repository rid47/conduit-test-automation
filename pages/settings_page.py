"""Page object for the user settings page (/settings)."""
from playwright.sync_api import Page

from pages.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.image_input = page.locator("input[formcontrolname='image']")
        self.username_input = page.locator("input[formcontrolname='username']")
        self.bio_textarea = page.locator("textarea[formcontrolname='bio']")
        self.email_input = page.locator("input[formcontrolname='email']")
        self.password_input = page.locator("input[formcontrolname='password']")
        self.update_button = page.get_by_role("button", name="Update Settings")

    def goto(self):
        self.page.goto("/settings")

    def update_settings(self):
        with self.page.expect_response(lambda r: r.url.endswith("/api/user") and r.request.method == "PUT") as resp_info:
            self.update_button.click()
        return resp_info.value

    def email_field_validity(self) -> bool:
        """True if the browser's native HTML5 constraint validation
        considers the current email input value well-formed."""
        return self.email_input.evaluate("el => el.validity.valid")
