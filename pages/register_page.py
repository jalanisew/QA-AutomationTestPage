from selenium.webdriver.common.by import By
from .base_page import BasePage

class RegisterPage(BasePage):
    FIRSTNAME = (By.NAME, "firstname")
    LASTNAME = (By.NAME, "lastname")
    EMAIL = (By.NAME, "email")
    LOGINNAME = (By.NAME, "loginname")
    PASSWORD = (By.NAME, "password")
    CONFIRM_PASSWORD = (By.NAME, "confirm")
    REGISTER_BTN = (By.XPATH, "//button[@title='Continue']")
    SUCCESS_MSG = (By.CSS_SELECTOR, ".heading1")

    def open_register(self, base_url: str):
        self.open(f"{base_url}/index.php?rt=account/create")

    def register(self, firstname, lastname, email, loginname, password):
        self.type(self.FIRSTNAME, firstname)
        self.type(self.LASTNAME, lastname)
        self.type(self.EMAIL, email)
        self.type(self.LOGINNAME, loginname)
        self.type(self.PASSWORD, password)
        self.type(self.CONFIRM_PASSWORD, password)
        self.click(self.REGISTER_BTN)

    def is_registered(self):
        return self.is_visible(self.SUCCESS_MSG)
