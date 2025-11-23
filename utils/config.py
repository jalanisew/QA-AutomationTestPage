from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Base URL of the site under test
BASE_URL = os.getenv("BASE_URL", "https://automationteststore.com")

# Credentials for login tests
USERNAME = os.getenv("USERNAME", "testuser")
PASSWORD = os.getenv("PASSWORD", "testpass")

# Run browser in headless mode (True/False)
HEADLESS = os.getenv("HEADLESS", "False") == "True"

# Default timeout for waits
DEFAULT_TIMEOUT = 15
