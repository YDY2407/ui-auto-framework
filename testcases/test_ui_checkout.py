"""
商品加购与结算 UI 自动化测试
演示三大企业级王炸亮点：
1. 使用 logged_in_page 夹具注入 Cookie 跳过登录页（提速！）
2. POM 页面对象封装，业务用例读起来像自然语言
3. 使用 Playwright page.route() 拦截后端 /api/checkout 接口并 Mock 返回 500，轻松测试前端异常容错！
"""
import json
import allure
import pytest
from playwright.sync_api import expect
from pages.shop_page import ShopPage


@allure.feature("Web UI - 加购与结算模块")
class TestUICheckout:
    @pytest.mark.smoke
    def test_add_to_cart_and_checkout_success(self, logged_in_page, mock_web_server):
        allure.dynamic.title("UI_ORDER_001 - 加购两件商品并成功结算")
        shop = ShopPage(logged_in_page, mock_web_server).open_shop()

        shop.add_keyboard()  # ¥399
        shop.add_mouse()     # ¥199

        expect(shop.cart_count).to_have_text("2")
        expect(shop.cart_total).to_have_text("598")

        shop.checkout()
        expect(shop.checkout_result).to_contain_text("下单成功！订单号：UI-ORD-20261125")

    @pytest.mark.negative
    def test_checkout_empty_cart_shows_warning(self, logged_in_page, mock_web_server):
        allure.dynamic.title("UI_ORDER_002 - 空购物车点击结算提示错误")
        shop = ShopPage(logged_in_page, mock_web_server).open_shop()
        shop.checkout()
        expect(shop.checkout_result).to_have_text("购物车为空，请先选择商品")

    @pytest.mark.mock
    def test_checkout_backend_500_mock(self, logged_in_page, mock_web_server):
        """
        面试王炸亮点：不改后端代码，用 Playwright 拦截网络请求模拟后端 500 宕机，
        验证前端是否优雅展示错误提示而不是白屏崩溃！
        """
        allure.dynamic.title("UI_MOCK_001 - 拦截结算接口模拟 500 异常，校验前端容错提示")

        def mock_500(route):
            route.fulfill(
                status=500,
                content_type="application/json",
                body=json.dumps({"code": 50000, "message": "支付网关超时，请稍后重试"}, ensure_ascii=False),
            )

        logged_in_page.route("**/api/checkout", mock_500)

        shop = ShopPage(logged_in_page, mock_web_server).open_shop()
        shop.add_keyboard()
        shop.checkout()

        expect(shop.checkout_result).to_have_text("下单失败：支付网关超时，请稍后重试")
