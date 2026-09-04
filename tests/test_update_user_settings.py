"""Update User Settings scenario."""
import allure
from playwright.sync_api import Page, expect

from api.api_client import ApiClient
from pages.profile_page import ProfilePage
from pages.settings_page import SettingsPage
from utils.data_generator import random_bio, random_image_url


@allure.epic("Conduit")
@allure.feature("Update User Settings")
class TestUpdateUserSettings:
    @allure.title("Updating bio and profile image with valid data persists")
    def test_update_settings_success(self, page: Page, registered_user: dict):
        settings = SettingsPage(page)
        new_bio = random_bio()
        new_image = random_image_url()

        with allure.step("Fill in a new bio and profile image URL"):
            settings.goto()
            settings.bio_textarea.fill(new_bio)
            settings.image_input.fill(new_image)

        with allure.step("Save and confirm the API call succeeded"):
            response = settings.update_settings()
            assert response.status == 200, f"Expected 200 OK, got {response.status}: {response.text()}"

        with allure.step("The new bio and avatar are visible on the public profile page (data persistence)"):
            # The Settings form itself never re-populates its fields on
            # load/reload (a genuine bug in this app, reproducible even via
            # direct API calls with no test involved), so persistence is
            # verified through the profile page, which does reflect it.
            profile = ProfilePage(page)
            profile.goto(registered_user["username"])
            profile.expect_bio_visible(new_bio)
            expect(profile.avatar).to_have_attribute("src", new_image)

    @allure.title("An invalid email format is flagged by client-side validation and not saved")
    def test_update_settings_invalid_email_is_rejected(self, page: Page, api_client: ApiClient, registered_user: dict):
        settings = SettingsPage(page)

        with allure.step("Enter a malformed email address"):
            settings.goto()
            settings.email_input.fill("not-a-valid-email-format")

        with allure.step("The browser's native email validation rejects it before it can be saved"):
            assert settings.email_field_validity() is False, "Malformed email was not flagged as invalid"

        with allure.step("The account's email on the server is unchanged"):
            current = api_client.get_current_user(registered_user["token"])
            assert current["email"] == registered_user["email"]
