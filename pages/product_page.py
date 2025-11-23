import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

class ProductPage:
    def __init__(self, driver, wait_time=12):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_time)
        self.screenshot_dir = "reports_screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    # Multiple possible Add-to-Cart button selectors
    ADD_TO_CART_CANDIDATES = [
        (By.CSS_SELECTOR, "a.cart"),
        (By.CSS_SELECTOR, "button[title*='Add']"),
        (By.CSS_SELECTOR, "input[value*='Add']"),
        (By.XPATH, "//a[contains(., 'Add to Cart')]"),
        (By.XPATH, "//button[contains(., 'Add to Cart')]"),
        (By.XPATH, "//input[contains(@value,'Add')]"),
    ]

    # Quantity input
    QTY_SELECTORS = [
        (By.CSS_SELECTOR, "input#product_quantity"),
        (By.CSS_SELECTOR, "input[name*='quantity']"),
    ]

    # Options
    OPTIONS_DROPDOWN = (By.CSS_SELECTOR, "select[name*='option']")
    OPTIONS_LIST = (By.CSS_SELECTOR, "select[name*='option'] option")

    # Success indicators (expanded)
    SUCCESS_ALERTS = [
        (By.CSS_SELECTOR, "div.alert-success"),
        (By.CSS_SELECTOR, "div.success"),
        (By.XPATH, "//div[contains(@class,'alert') and contains(.,'Success')]"),
    ]

    # Cart total indicators (expanded)
    CART_TOTAL_CANDIDATES = [
        (By.CSS_SELECTOR, "#cart_total"),
        (By.CSS_SELECTOR, "div#cart span.label"),
        (By.CSS_SELECTOR, "a[href*='checkout/cart'] span.label"),
        (By.CSS_SELECTOR, "span#cart-total"),
    ]

    def _screenshot(self, name):
        path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        self.driver.save_screenshot(path)
        return path

    def _dump_page(self, name):
        path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        return path

    # ------------------------------------------
    # QUANTITY
    # ------------------------------------------
    def set_quantity(self, qty):
        for sel in self.QTY_SELECTORS:
            try:
                elem = self.driver.find_element(*sel)
                elem.clear()
                elem.send_keys(str(qty))
                print(f" Quantity set to {qty}")
                return True
            except:
                continue
        print(" Quantity box not found.")
        return False

    # ------------------------------------------
    # OPTIONS
    # ------------------------------------------
    def select_option_if_required(self):
        """Select first available option (if product requires it)."""
        try:
            dropdown = self.driver.find_element(*self.OPTIONS_DROPDOWN)
            options = dropdown.find_elements(*self.OPTIONS_LIST)
            for opt in options:
                if opt.get_attribute("value"):
                    opt.click()
                    print(" Selected required product option.")
                    return True
        except:
            return False
        return False

    # ------------------------------------------
    # ADD BUTTON FINDER
    # ------------------------------------------
    def _find_add_button(self):
        for sel in self.ADD_TO_CART_CANDIDATES:
            try:
                elems = self.driver.find_elements(*sel)
                for e in elems:
                    if e.is_displayed() and e.is_enabled():
                        return e
            except:
                continue
        return None

    # ------------------------------------------
    # CLICK ADD TO CART
    # ------------------------------------------
    def click_add_to_cart(self):
        # First select option (if needed)
        self.select_option_if_required()

        btn = self._find_add_button()
        if not btn:
            ss = self._screenshot("add_btn_not_found")
            src = self._dump_page("add_btn_source")
            raise NoSuchElementException(
                f"Add-to-Cart button not found.\nScreenshot: {ss}\nPage Source: {src}"
            )

        # Scroll to button
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
        except:
            pass

        # Try clicking normally -> fallback to JS click, with retry
        for attempt in range(2):
            try:
                try:
                    btn.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", btn)
                break
            except Exception as e:
                if attempt == 1:
                    ss = self._screenshot("add_click_failed")
                    src = self._dump_page("add_click_failed_source")
                    raise Exception(
                        f"Could not click Add to Cart.\nScreenshot: {ss}\nPage Source: {src}\nError: {e}"
                    )
                time.sleep(1)

        # ------------------------------------------
        # VERIFY CART UPDATED
        # ------------------------------------------
        try:
            self.wait.until(
                lambda d: (
                    any(len(d.find_elements(*sel)) > 0 for sel in self.SUCCESS_ALERTS)
                    or self._cart_has_items(d)
                )
            )
            print(" Add to Cart succeeded.")
            return True

        except TimeoutException:
            ss = self._screenshot("add_failed")
            src = self._dump_page("add_failed_source")
            raise TimeoutException(
                f"Add to Cart did NOT update.\nScreenshot: {ss}\nPage Source: {src}"
            )

    # ------------------------------------------
    # CHECK IF CART TOTAL HAS ITEMS
    # ------------------------------------------
    def _cart_has_items(self, driver):
        for sel in self.CART_TOTAL_CANDIDATES:
            try:
                elems = driver.find_elements(*sel)
                for e in elems:
                    txt = e.text.strip().lower()
                    if txt and "0 item" not in txt and txt != "0":
                        return True
            except:
                continue
        return False
