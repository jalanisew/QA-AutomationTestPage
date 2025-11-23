import pytest
from selenium import webdriver
from pages.product_page import ProductPage
from pages.cart_page import CartPage

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_add_to_cart_and_verify(driver):
    driver.get("https://automationteststore.com/index.php?product_id=50&rt=product/product")

    product = ProductPage(driver)
    cart = CartPage(driver)

    product.set_quantity(2)
    assert product.click_add_to_cart() is True

    cart.go_to_cart()
    assert len(cart.get_product_names()) > 0
    assert cart.get_quantities()[0] == "2"

