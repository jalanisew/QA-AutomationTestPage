import time
from utils import config
from pages.register_page import RegisterPage

def test_register_success(driver):
    register_page = RegisterPage(driver, timeout=config.DEFAULT_TIMEOUT)

    print(" Opening registration page...")
    register_page.open_register(config.BASE_URL)

    # Unique login name/email each run to avoid conflicts
    timestamp = int(time.time())
    email = f"test{timestamp}@example.com"
    loginname = f"user{timestamp}"

    print(" Registering new account...")
    register_page.register(
        firstname="Test",
        lastname="User",
        email=email,
        loginname=loginname,
        password="Password123"
    )

    print(" Verifying registration success...")
    assert register_page.is_registered(), "Registration failed — success message not found"
