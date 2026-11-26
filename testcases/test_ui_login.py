"""
登录页 UI 自动化测试（POM 模式 + 参数化）
注意：全程零 time.sleep()！全部使用 Playwright 的 expect() 智能自动等待断言。
"""
import re
import allure
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.shop_page import ShopPage


@allure.feature("Web UI - 登录模块")
class TestUILogin:
    @pytest.mark.smoke
    def test_login_success(self, page, mock_web_server):
        allure.dynamic.title("UI_LOGIN_001 - 正常登录成功并跳转商城大厅")
        login_page = LoginPage(page, mock_web_server).open_login()
        login_page.login("tester", "Password123")

        # Playwright expect 自动等待 URL 跳转与元素出现
        expect(page).to_have_url(re.compile(r".*/shop$"))
        shop_page = ShopPage(page, mock_web_server)
        expect(shop_page.current_user).to_have_text("tester")

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "username, password, expected_err",
        [
            ("tester", "WrongPwd", "用户名或密码错误"),
            ("", "Password123", "用户名和密码不能为空"),
            ("tester", "", "用户名和密码不能为空"),
        ],
        ids=["密码错误", "用户名为空", "密码为空"],
    )
    def test_login_negative(self, page, mock_web_server, username, password, expected_err):
        login_page = LoginPage(page, mock_web_server).open_login()
        login_page.login(username, password)

        expect(login_page.error_msg).to_have_text(expected_err)
        expect(page).to_have_url(re.compile(r".*/login$"))
