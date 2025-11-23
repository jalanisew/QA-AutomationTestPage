from utils import config

def test_login_success(driver, login_page):
    print(" Opening login page...")
    login_page.open_login(config.BASE_URL)

    print(" Logging in with:", config.USERNAME)
    login_page.login(config.USERNAME, config.PASSWORD)

    print(" Verifying login success...")
    assert login_page.is_logged_in(), "Login failed — welcome message not found"
