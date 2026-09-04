"""Filter Articles by Tag scenario."""
import allure
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@allure.epic("Conduit")
@allure.feature("Filter Articles by Tag")
class TestFilterArticlesByTag:
    @allure.title("Clicking a tag filters the feed to only articles that carry that tag")
    def test_filter_by_tag_shows_only_matching_articles(self, page: Page):
        home = HomePage(page)

        with allure.step("Load the home page and pick a real tag from the popular-tags sidebar"):
            home.goto()
            expect(home.tag_pills.first).to_be_visible()
            tag_name = home.tag_pills.first.text_content().strip()

        with allure.step(f"Click the '{tag_name}' tag"):
            home.click_tag(tag_name)

        with allure.step("The matching feed tab becomes active"):
            home.expect_active_tab(tag_name)

        with allure.step("Every visible article carries the selected tag"):
            expect(home.article_previews.first).to_be_visible()
            count = home.article_previews.count()
            for i in range(count):
                tags = [t.strip() for t in home.article_preview_tags(i)]
                assert tag_name in tags, f"Article at index {i} is missing tag '{tag_name}': {tags}"

    @allure.title("Filtering by a tag with no matching articles shows the empty-state message")
    def test_filter_by_tag_with_no_matches_shows_empty_state(self, page: Page):
        home = HomePage(page)

        with allure.step("Load the home page and note an existing tag to click"):
            home.goto()
            expect(home.tag_pills.first).to_be_visible()
            tag_name = home.tag_pills.first.text_content().strip()

        with allure.step("Simulate a tag with zero matching articles by stubbing the filtered-feed API call"):
            page.route(
                lambda url: "/api/articles" in url and "tag=" in url,
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"articles": [], "articlesCount": 0}',
                ),
            )
            home.click_tag(tag_name)

        with allure.step("The empty-state message is displayed instead of any article"):
            expect(home.empty_state_message).to_be_visible()
            # The empty-state placeholder itself carries the .article-preview
            # class, so assert on the absence of real article links instead
            # of the raw .article-preview count.
            expect(home.article_previews.locator("a.preview-link")).to_have_count(0)
