from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME = (By.NAME, "loginname")
    PASSWORD = (By.NAME, "password")
    LOGIN_BTN = (By.XPATH, "//button[@title='Login']")
    SUCCESS_MSG = (By.CSS_SELECTOR, ".heading1")

    def open_login(self, base_url: str):
        self.open(f"{base_url}/index.php?rt=account/login")

    def login(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BTN)

    def is_logged_in(self):
        return self.is_visible(self.SUCCESS_MSG)
