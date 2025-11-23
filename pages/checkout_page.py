import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CheckoutPage:
    def __init__(self, driver, wait_time=12, screenshot_dir="reports_screenshots"):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_time)
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    # Guest checkout candidates
    GUEST_RADIOS = [
        (By.CSS_SELECTOR, "input#accountFrm_accountguest"),
        (By.CSS_SELECTOR, "input[name='account'][value='guest']"),
        (By.XPATH, "//input[contains(@value,'guest')]"),
    ]

    # Continue buttons (fallbacks)
    CONTINUE_BUTTONS = [
        (By.CSS_SELECTOR, "button[title='Continue']"),
        (By.CSS_SELECTOR, "input[value='Continue']"),
        (By.CSS_SELECTOR, "button.btn.btn-orange.pull-right"),
        (By.XPATH, "//button[contains(text(),'Continue')]"),
        (By.XPATH, "//a[contains(text(),'Continue')]"),
        (By.CSS_SELECTOR, "button[title='Next'], button[title='Proceed']"),
    ]

    # Billing fields
    FIRST_NAME = [(By.CSS_SELECTOR, "input#guestFrm_firstname"),
                  (By.CSS_SELECTOR, "input[name*='firstname']")]
    LAST_NAME = [(By.CSS_SELECTOR, "input#guestFrm_lastname"),
                 (By.CSS_SELECTOR, "input[name*='lastname']")]
    EMAIL = [(By.CSS_SELECTOR, "input#guestFrm_email"),
             (By.CSS_SELECTOR, "input[name*='email']")]
    ADDRESS = [(By.CSS_SELECTOR, "input#guestFrm_address_1"),
               (By.CSS_SELECTOR, "input[name*='address']")]
    CITY = [(By.CSS_SELECTOR, "input#guestFrm_city"),
            (By.CSS_SELECTOR, "input[name*='city']")]
    POSTCODE = [(By.CSS_SELECTOR, "input#guestFrm_postcode"),
                (By.CSS_SELECTOR, "input[name*='postcode'], input[name*='zip']")]
    COUNTRY = [(By.CSS_SELECTOR, "select#guestFrm_country_id"),
               (By.CSS_SELECTOR, "select[name*='country']")]
    REGION = [(By.CSS_SELECTOR, "select#guestFrm_zone_id"),
              (By.CSS_SELECTOR, "select[name*='zone'], select[name*='state']")]

    # Payment and terms
    TERMS_CHECKBOX = [
        (By.NAME, "agree"),
        (By.ID, "agree"),
        (By.CSS_SELECTOR, "input[type='checkbox'][name='agree']"),
        (By.XPATH, "//label[contains(.,'I have read')]/input")
    ]
    PAYMENT_METHODS = [
        (By.CSS_SELECTOR, "input[name='payment_method'][value='cod']"),
        (By.XPATH, "//input[@name='payment_method' and contains(@value,'cod')]"),
        (By.XPATH, "//input[@name='payment_method' and contains(@value,'cash')]"),
        (By.XPATH, "//label[contains(.,'Cash On Delivery')]//input"),
        (By.XPATH, "//label[contains(.,'COD')]//input"),
        (By.XPATH, "//div[contains(@class,'payment')]//input[@type='radio']"),
        (By.XPATH, "//input[@type='radio' and (contains(@id,'cod') or contains(@value,'cod'))]"),
        (By.XPATH, "//div[@id='payment-method']//input[@type='radio']"),
    ]
    PAYMENT_SECTIONS = [
        (By.ID, "payment-method"),
        (By.ID, "checkout_payment_method"),
        (By.ID, "payment"),
        (By.CSS_SELECTOR, "div.checkout-payment"),
        (By.XPATH, "//div[contains(@id,'payment')]"),
        (By.XPATH, "//div[contains(@class,'payment')]"),
    ]

    # Confirm order buttons
    CONFIRM_BUTTONS = [
        (By.CSS_SELECTOR, "button#checkout_confirm"),
        (By.CSS_SELECTOR, "button#button-confirm"),
        (By.CSS_SELECTOR, "button[title='Confirm Order']"),
        (By.CSS_SELECTOR, "button[title='Place Order']"),
        (By.XPATH, "//button[contains(text(),'Confirm')]"),
        (By.XPATH, "//button[contains(text(),'Place Order')]"),
    ]

    def _screenshot(self, name):
        p = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        self.driver.save_screenshot(p)
        return p

    def click_any(self, selectors, timeout=15):
        """Try all selectors, scroll into view, JS click fallback."""
        end = time.time() + timeout
        while time.time() < end:
            for sel in selectors:
                try:
                    elems = self.driver.find_elements(*sel)
                except Exception:
                    elems = []
                for e in elems:
                    if e.is_displayed():
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", e)
                            e.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", e)
                        return True
            time.sleep(0.4)
        return False

    def choose_guest_checkout(self):
        if self.click_any(self.GUEST_RADIOS):
            print(" Guest checkout selected.")
            self.click_any(self.CONTINUE_BUTTONS)
            return True
        print(" Guest checkout step skipped.")
        return True

    def fill_billing(self, data=None):
        d = data or {
            "first": "Test",
            "last": "User",
            "email": f"test{int(time.time())}@mail.com",
            "address": "123 Test Street",
            "city": "Colombo",
            "postcode": "10000",
            "country": "Sri Lanka"
        }

        def fill(field_list, value):
            for sel in field_list:
                try:
                    e = self.driver.find_element(*sel)
                    e.clear()
                    e.send_keys(value)
                    return True
                except:
                    continue
            return False

        fill(self.FIRST_NAME, d["first"])
        fill(self.LAST_NAME, d["last"])
        fill(self.EMAIL, d["email"])
        fill(self.ADDRESS, d["address"])
        fill(self.CITY, d["city"])
        fill(self.POSTCODE, d["postcode"])

        # Select country
        for sel in self.COUNTRY:
            try:
                dropdown = self.driver.find_element(*sel)
                opts = dropdown.find_elements(By.TAG_NAME, "option")
                for o in opts:
                    if d["country"].lower() in o.text.lower():
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                            dropdown, o.get_attribute("value")
                        )
                        break
            except:
                continue

        print(" Billing info filled.")

        if not self.click_any(self.CONTINUE_BUTTONS):
            ss = self._screenshot("billing_continue_fail")
            raise TimeoutException(f"Could not continue after billing. Screenshot: {ss}")

    def continue_shipping(self):
        if not self.click_any(self.CONTINUE_BUTTONS):
            ss = self._screenshot("shipping_continue_fail")
            raise TimeoutException(f"Failed to continue shipping. Screenshot: {ss}")
        print(" Shipping continued.")

    def continue_payment(self):
        # Wait for any payment section to be visible
        found_section = False
        for sel in self.PAYMENT_SECTIONS:
            try:
                self.wait.until(EC.visibility_of_element_located(sel))
                found_section = True
                break
            except TimeoutException:
                continue
        if not found_section:
            ss = self._screenshot("payment_section_not_visible")
            raise TimeoutException(f"Payment section not visible. Screenshot: {ss}")

        # Select payment method
        if not self.click_any(self.PAYMENT_METHODS):
            ss = self._screenshot("payment_method_fail")
            raise TimeoutException(f"Payment method not found. Screenshot: {ss}")
        print(" Payment method selected (COD).")

        # Tick terms checkbox
        if not self.click_any(self.TERMS_CHECKBOX):
            ss = self._screenshot("terms_checkbox_fail")
            raise TimeoutException(f"Terms checkbox not found. Screenshot: {ss}")
        print(" Terms accepted.")

        if not self.click_any(self.CONTINUE_BUTTONS):
            ss = self._screenshot("payment_continue_fail")
            raise TimeoutException(f"Failed to continue payment. Screenshot: {ss}")
        print(" Payment continued.")

    def confirm_order(self):
        if not self.click_any(self.CONFIRM_BUTTONS):
            ss = self._screenshot("confirm_fail")
            raise TimeoutException(f"Failed to confirm order. Screenshot: {ss}")
        print(" Order confirmed.")
