import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CartPage:
    CART_URL = "https://automationteststore.com/index.php?rt=checkout/cart"

    # Checkout button candidates
    CHECKOUT_BTN_CANDIDATES = [
        (By.CSS_SELECTOR, "a[href*='checkout'], a.checkout, a.btn.btn-primary"),
        (By.CSS_SELECTOR, "button[title='Checkout'], button#checkout"),
        (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]"),
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]"),
    ]

    # Product name candidates (many fallbacks)
    PRODUCT_NAME_CANDIDATES = [
        (By.CSS_SELECTOR, "td.name a"),
        (By.CSS_SELECTOR, "td.product-name a"),
        (By.CSS_SELECTOR, "td[class*='name'] a"),
        (By.CSS_SELECTOR, "tr.cart_item td a"),               # some themes
        (By.CSS_SELECTOR, "table.cart td a"),                 # generic
        (By.CSS_SELECTOR, "table tbody tr td:nth-child(2) a") # fallback: 2nd column anchor
    ]

    # Quantity inputs
    QTY_INPUT = (By.CSS_SELECTOR, "input[name*='quantity'], input[name*='qty']")

    # Generic product row selector
    PRODUCT_ROW_CANDIDATES = [
        (By.CSS_SELECTOR, "table.cart tbody tr"),
        (By.CSS_SELECTOR, "table tbody tr"),
        (By.CSS_SELECTOR, "tr.cart_item"),
    ]

    EMPTY_CART_MESSAGES = [
        "your shopping cart is empty",
        "your cart is empty",
        "no products in the cart",
        "there are no items in your shopping cart",
    ]

    def __init__(self, driver, wait_time=12, screenshot_dir="reports_screenshots"):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_time)
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _screenshot(self, name):
        path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        try:
            self.driver.save_screenshot(path)
        except Exception:
            pass
        return path

    def _dump_page(self, name):
        path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.html")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass
        return path

    # -------------------------------
    # OPEN CART
    # -------------------------------
    def go_to_cart(self):
        self.driver.get(self.CART_URL)

        # Wait for either a table or known empty-cart text to appear
        try:
            self.wait.until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "table") or
                          any(msg in d.page_source.lower() for msg in self.EMPTY_CART_MESSAGES)
            )
        except Exception:
            # If the generic wait fails, proceed — we'll catch missing products later
            pass

        print(" Cart page opened.")

    # -------------------------------
    # CLICK CHECKOUT
    # -------------------------------
        
    def click_checkout(self):

        REAL_CHECKOUT_SELECTORS = [
        
            (By.CSS_SELECTOR, "a[href*='checkout/checkout']"),

            # Backups — same destination
            (By.XPATH, "//a[contains(@href,'checkout/checkout')]"),
            (By.XPATH, "//a[contains(.,'Checkout') and contains(@class,'btn')]"),
        ]

        for sel in REAL_CHECKOUT_SELECTORS:
            try:
                elems = self.driver.find_elements(*sel)
                for e in elems:
                    if e.is_displayed() and e.is_enabled():
                        # Scroll into view
                        try:
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});", e
                            )
                        except:
                            pass

                        # Try normal click → fallback to JS click
                        try:
                            e.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", e)

                        print(" Correct Checkout button clicked:", sel)
                        return True
            except:
                continue

        # ----- If still not found, direct navigation (safe fallback) -----
        print(" REAL Checkout button not found. Navigating directly.")
        self.driver.get("https://automationteststore.com/index.php?rt=checkout/checkout")
        return True


    # -------------------------------
    # GET PRODUCT NAMES
    # -------------------------------
    def get_product_names(self):
        # try candidate selectors first
        names = []
        for sel in self.PRODUCT_NAME_CANDIDATES:
            try:
                elems = self.driver.find_elements(*sel)
            except Exception:
                elems = []
            for e in elems:
                try:
                    txt = e.text.strip()
                    if txt:
                        names.append(txt)
                except Exception:
                    continue
            if names:
                print("Products found using selector:", sel, names)
                return names

        # fallback: parse table rows and take 2nd-column anchor text
        for sel in self.PRODUCT_ROW_CANDIDATES:
            try:
                rows = self.driver.find_elements(*sel)
            except Exception:
                rows = []
            for r in rows:
                try:
                    # try to get anchor in 2nd td
                    anchor = None
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) >= 2:
                        anchors = tds[1].find_elements(By.TAG_NAME, "a")
                        if anchors:
                            anchor = anchors[0]
                    # fallback: any anchor inside row
                    if not anchor:
                        anchors = r.find_elements(By.TAG_NAME, "a")
                        anchor = anchors[0] if anchors else None
                    if anchor:
                        txt = anchor.text.strip()
                        if txt:
                            names.append(txt)
                except Exception:
                    continue
            if names:
                print(" Products parsed from rows:", names)
                return names

        # Last resort: try searching for product title elements anywhere
        try:
            candidates = self.driver.find_elements(By.XPATH, "//*[contains(@class,'product') and contains(., 'product')]/a")
            for e in candidates:
                try:
                    if e.is_displayed() and e.text.strip():
                        names.append(e.text.strip())
                except Exception:
                    continue
            if names:
                print(" Products found via generic fallback:", names)
                return names
        except Exception:
            pass

        # Nothing found — save debug artifacts and return empty list
        ss = self._screenshot("cart_no_products")
        src = self._dump_page("cart_no_products_source")
        print(f" No products found in cart. Saved screenshot: {ss} page source: {src}")
        return []

    # -------------------------------
    # GET QUANTITIES
    # -------------------------------
    def get_quantities(self):
        qtys = []
        try:
            inputs = self.driver.find_elements(*self.QTY_INPUT)
            for i in inputs:
                try:
                    v = i.get_attribute("value")
                    qtys.append(v)
                except Exception:
                    continue
        except Exception:
            pass
        print(" Quantities:", qtys)
        return qtys
