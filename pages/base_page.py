"""
POM 基类：封装所有页面通用的基础能力（导航、截图、等待等）
"""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8900"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, path: str = "/"):
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")
        return self
