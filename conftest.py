# conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import config
from pages.login_page import LoginPage

@pytest.fixture
def driver():
    options = Options()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")

    # Disable autofill and password manager
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    with webdriver.Chrome(options=options) as d:
        yield d

@pytest.fixture
def login_page(driver):
    return LoginPage(driver, timeout=config.DEFAULT_TIMEOUT)
