# QA-AutomationTestPage
This project contains a Python-based Selenium automation suite for testing core user flows onautomationteststore.com.  
The test cases cover essential e-commerce functions including user registration, login, adding products to the cart, and the guest checkout process.

 Features Covered
1. User Registration
- Navigates to registration page
- Fills all mandatory fields
- Validates account creation

2. User Login
- Verifies login form
- Handles valid and invalid login attempts
- Confirms successful authentication

3. Add to Cart
- Opens product page directly
- Handles quantity changes
- Selects required dropdown options (if available)
- Adds items to the cart with verification

4. Cart Page
- Extracts product names and quantities
- Validates cart summary
- Opens checkout using multiple selector fallbacks

5. Guest Checkout
- Selects guest checkout mode
- Fills billing details
- Continues through shipping & payment sections
- Attempts an order confirmation


Tech Stack

⦁	Python 3
⦁	Selenium WebDriver
⦁	pytest
⦁	WebDriverWait / Expected Conditions
⦁	Page Object Model (POM) for maintainability


Project Structure

AutomationTestStore-Automation/
│
├── pages/
│ ├── login_page.py
│ ├── register_page.py
│ ├── product_page.py
│ ├── cart_page.py
│ ├── checkout_page.py
│ └── order_success_page.py
│
├── tests/
│ ├── test_login.py
│ ├── test_register.py
│ ├── test_cart.py
│ └── test_checkout.py
│
├── reports_screenshots/ (ignored in repo)
├── requirements.txt
├── README.md
└── .gitignore


Running the Tests

1. Create virtual environment
powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1


2. Install dependencies
pip install -r requirements.txt


3. Run all tests
pytest -v


4. Run a specific test file
pytest tests/test_cart.py -v


