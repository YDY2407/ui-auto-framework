"""
登录页 Page Object（POM 分层示例）
原则：
1. 页面元素定位器集中管理（优先用 data-testid，最稳、不怕改样式）
2. 封装业务动作 login()，用例层不直接写死 locator
"""
from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8900"):
        super().__init__(page, base_url)
        self.username_input = page.get_by_test_id("username-input")
        self.password_input = page.get_by_test_id("password-input")
        self.login_btn = page.get_by_test_id("login-btn")
        self.error_msg = page.get_by_test_id("error-msg")

    def open_login(self):
        return self.open("/login")

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()
