"""Shared behavior for all page objects."""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page
