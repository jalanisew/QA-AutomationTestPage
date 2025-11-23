import os
import time
import pytest
from selenium import webdriver

from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.order_success_page import OrderSuccessPage

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


def test_guest_checkout(driver):
    # Product page
    driver.get("https://automationteststore.com/index.php?product_id=50&rt=product/product")

    product = ProductPage(driver)
    cart = CartPage(driver)
    checkout = CheckoutPage(driver)
    success = OrderSuccessPage(driver)

    # Add to cart
    product.set_quantity(1)
    assert product.click_add_to_cart() is True

    # Go to cart
    cart.go_to_cart()
    names = cart.get_product_names()
    assert len(names) > 0, "Cart is empty after adding product."

    # Checkout
    cart.click_checkout()
    checkout.choose_guest_checkout()
    checkout.fill_billing()
    checkout.continue_shipping()
    checkout.continue_payment()
    checkout.confirm_order()

    # Success page
    assert success.is_success(), "Order success page NOT detected!"
