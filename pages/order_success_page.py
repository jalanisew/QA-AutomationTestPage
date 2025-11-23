import os
import time
from selenium.webdriver.common.by import By

class OrderSuccessPage:
    SUCCESS_TEXTS = [
        "your order has been processed",
        "thank you for your order",
        "order confirmation",
        "successfully completed",
        "order has been placed",
        "purchase complete",
    ]

    SUCCESS_LOCATORS = [
        (By.XPATH, "//h1[contains(.,'Processed')]"),
        (By.XPATH, "//h1[contains(.,'Success')]"),
        (By.XPATH, "//h1[contains(.,'Order')]"),
        (By.CSS_SELECTOR, "div.success, div.alert-success"),
        (By.CSS_SELECTOR, "div.checkout-success"),
    ]

    def __init__(self, driver, screenshot_dir="reports_screenshots"):
        self.driver = driver
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _screenshot(self, name):
        path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        self.driver.save_screenshot(path)
        return path

    def is_success(self):
        # Check UI headings / success containers
        for sel in self.SUCCESS_LOCATORS:
            try:
                els = self.driver.find_elements(*sel)
                for e in els:
                    if e.is_displayed():
                        print(f" Success element found: {sel}")
                        return True
            except Exception:
                continue

        # Check page text for known success phrases
        page = self.driver.page_source.lower()
        for t in self.SUCCESS_TEXTS:
            if t in page:
                print(f" Success text matched: '{t}'")
                return True

        # If nothing matched, capture screenshot for debugging
        ss = self._screenshot("order_success_not_found")
        print(f" No success indicators found. Screenshot: {ss}")
        return False
