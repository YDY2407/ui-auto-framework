"""
商品大厅与结算页 Page Object
"""
from playwright.sync_api import Page
from pages.base_page import BasePage


class ShopPage(BasePage):
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8900"):
        super().__init__(page, base_url)
        self.current_user = page.get_by_test_id("current-user")
        self.cart_count = page.get_by_test_id("cart-count")
        self.cart_total = page.get_by_test_id("cart-total")
        self.add_keyboard_btn = page.get_by_test_id("add-keyboard")
        self.add_mouse_btn = page.get_by_test_id("add-mouse")
        self.checkout_btn = page.get_by_test_id("checkout-btn")
        self.checkout_result = page.get_by_test_id("checkout-result")

    def open_shop(self):
        return self.open("/shop")

    def add_keyboard(self):
        self.add_keyboard_btn.click()

    def add_mouse(self):
        self.add_mouse_btn.click()

    def checkout(self):
        self.checkout_btn.click()
