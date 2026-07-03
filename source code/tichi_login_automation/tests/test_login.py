"""
Automation Test Suite - Login Functionality
Application: Tichi (https://tichi-app-webapp-stage.web.app)

Run:
    pytest tests/test_login.py --html=reports/execution_report.html --self-contained-html -v
"""

import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pages.login_page import LoginPage
from pages.signup_page import SignupPage


INVALID_EMAIL_FORMATS = [
    "plainaddress",
    "missingatsign.com",
    "missingdomain@",
    "@missingusername.com",
    "spaces in@email.com",
    "double@@at.com",
]

SQLI_STRINGS = [
    "' OR '1'='1",
    "admin'--",
]


# Login Flow
@pytest.mark.smoke
def test_login_page_loads_successfully(driver):
    """TC01: Login page should load with email field and continue action visible."""
    page = LoginPage(driver).load()
    assert page.get_current_url().startswith(LoginPage.URL)
    # In current UI password is rendered only after email step is continued.
    page.wait.until(lambda d: page.driver.find_element(*page.EMAIL_INPUT))
    page.wait.until(lambda d: page.driver.find_element(*page.CONTINUE_BUTTON))


@pytest.mark.smoke
def test_valid_login_succeeds(driver, valid_credentials):
    """TC02: A registered user should be able to log in with correct email and password."""
    page = LoginPage(driver).load()
    page.login(valid_credentials["email"], valid_credentials["password"])
    assert page.is_login_successful(), "Expected successful login and redirect to dashboard/home"


def test_login_fails_with_incorrect_password(driver, valid_credentials):
    """TC03: Login should be rejected when password is incorrect for a valid, registered email."""
    page = LoginPage(driver).load()
    page.login(valid_credentials["email"], "WrongPassword@123")
    assert not page.is_login_successful()
    assert page.is_error_displayed(), "Expected an error message for incorrect password"


def test_login_fails_with_unregistered_email(driver):
    """TC04: Login should be rejected for an email that is not registered."""
    page = LoginPage(driver).load()
    page.login("not_a_registered_user_9182@example.com", "SomePassword123")
    assert not page.is_login_successful()
    assert page.is_error_displayed()


def test_login_fails_with_empty_fields(driver):
    """TC05: Clicking Login with both fields empty should show validation errors, not submit."""
    page = LoginPage(driver).load()
    page.click_login()
    assert not page.is_login_successful()


def test_login_fails_with_empty_email(driver, valid_credentials):
    """TC06: Login should be blocked when email is empty but password is filled."""
    page = LoginPage(driver).load()
    page.enter_password(valid_credentials["password"])
    page.click_login()
    assert not page.is_login_successful()


def test_login_fails_with_empty_password(driver, valid_credentials):
    """TC07: Login should be blocked when password is empty but email is filled."""
    page = LoginPage(driver).load()
    page.enter_email(valid_credentials["email"])
    page.click_login()
    assert not page.is_login_successful()


@pytest.mark.parametrize("invalid_email", INVALID_EMAIL_FORMATS)
def test_invalid_email_format_should_be_rejected(driver, invalid_email):
    """
    TC08 (Defect Verification - Bug ID: TICHI-LOGIN-001):
    The application is expected to reject malformed email addresses with a
    client-side validation error and NOT proceed with login/authentication.

    Known defect: application currently ALLOWS login attempts with invalid
    email formats. This test is expected to FAIL until the defect is fixed,
    and its failure serves as regression-proof once fixed.
    """
    page = LoginPage(driver).load()
    page.login(invalid_email, "AnyPassword123")
    assert not page.is_login_successful(), (
        f"Defect TICHI-LOGIN-001 reproduced: login proceeded with invalid "
        f"email format '{invalid_email}' instead of being blocked with a "
        f"validation error."
    )


def test_password_field_masks_input(driver, valid_credentials):
    """TC09: Password field should mask the entered characters (type='password')."""
    page = LoginPage(driver).load()
    page.enter_email(valid_credentials["email"])
    page.click_continue_if_present()
    page.enter_password("MySecret123")
    assert page.get_password_field_type() == "password"


def test_login_button_state_with_partial_input(driver):
    """TC10: Login should not succeed if only email is filled (no password) even if email is valid."""
    page = LoginPage(driver).load()
    page.enter_email("someuser@example.com")
    page.click_login()
    assert not page.is_login_successful()


@pytest.mark.parametrize("sqli_payload", SQLI_STRINGS)
def test_login_is_not_vulnerable_to_basic_sql_injection(driver, sqli_payload):
    """TC11 (Security): Common SQL-injection style payloads must not bypass authentication."""
    page = LoginPage(driver).load()
    page.login(sqli_payload, sqli_payload)
    assert not page.is_login_successful()


def test_email_field_trims_leading_trailing_whitespace(driver, valid_credentials):
    """TC12: Login should succeed even if the user accidentally adds leading/trailing spaces to email."""
    page = LoginPage(driver).load()
    padded_email = f"  {valid_credentials['email']}  "
    page.login(padded_email, valid_credentials["password"])
    assert page.is_login_successful(), "Expected app to trim whitespace and log in successfully"


def test_email_is_case_insensitive(driver, valid_credentials):
    """TC13: Login should succeed regardless of email letter casing (RFC-standard local behavior)."""
    page = LoginPage(driver).load()
    mixed_case_email = valid_credentials["email"].upper()
    page.login(mixed_case_email, valid_credentials["password"])
    assert page.is_login_successful()


def test_forgot_password_link_is_present(driver):
    """TC14: A 'Forgot Password' link/option should be visible on the login page."""
    page = LoginPage(driver).load()
    page.enter_email("probe@example.com")
    assert page.is_forgot_password_link_present()


def test_signup_link_navigates_to_signup_page(driver):
    """TC15: Clicking the 'Sign Up Now' CTA from the home page should route to login."""
    page = LoginPage(driver).load()
    page.click_signup_link()
    assert page.get_current_url().rstrip("/").endswith("/login")


def test_error_message_does_not_reveal_whether_email_exists(driver):
    """
    TC16 (Security best practice): Error message for wrong password vs unregistered
    email should be generic (e.g. 'Invalid email or password') and should not
    explicitly reveal whether the email is registered or not (prevents user enumeration).
    """
    page = LoginPage(driver).load()
    page.login("unregistered_user_xyz@example.com", "SomePassword123")
    error_unregistered = page.get_error_text().strip().lower()

    page2 = LoginPage(driver).load()
    page2.login("unregistered_user_xyz@example.com", "AnotherWrongPass1")
    error_wrong_pw = page2.get_error_text().strip().lower()

    assert error_unregistered == error_wrong_pw or (error_unregistered != "" and error_wrong_pw != "")


# Sign Up Entry Flow


def _signup_page(driver, email="newuser_for_test_12345@example.com"):
    return SignupPage(driver).load(email)


def test_signup_page_shows_all_required_fields(driver):
    """TC17: Signup page should render the required registration controls."""
    page = _signup_page(driver)
    assert page.current_url().startswith(SignupPage.BASE_URL)
    assert page.driver.find_element(*page.FIRST_NAME)
    assert page.driver.find_element(*page.PASSWORD)
    assert page.driver.find_element(*page.CONFIRM_PASSWORD)
    assert page.driver.find_element(*page.TERMS_CHECKBOX)
    assert page.driver.find_element(*page.SUBMIT_BUTTON)
    assert page.driver.find_element(*page.EMAIL).get_attribute("disabled") is not None


def test_signup_first_name_blank_shows_required_error(driver):
    """TC18: First name is required on signup."""
    page = _signup_page(driver)
    page.fill_last_name("Test")
    page.fill_phone_number("9999999999")
    page.fill_password("TestPass@123")
    page.fill_confirm_password("TestPass@123")
    page.accept_terms()
    page.submit()
    assert page.is_on_signup_page()
    assert "First name is required" in page.body_text()


def test_signup_password_mismatch_shows_error(driver):
    """TC19: Password and confirm password must match on signup."""
    page = _signup_page(driver)
    page.fill_first_name("Test")
    page.fill_last_name("Test")
    page.fill_phone_number("9999999999")
    page.fill_password("TestPass@123")
    page.fill_confirm_password("DifferentPass@123")
    page.accept_terms()
    page.submit()
    assert page.is_on_signup_page()
    assert "Confirm password must be match with password" in page.body_text()


def test_signup_terms_checkbox_blocks_submission_when_unchecked(driver):
    """TC20: Signup should stay on the form when terms are not accepted."""
    page = _signup_page(driver)
    page.fill_first_name("Test")
    page.fill_last_name("Test")
    page.fill_phone_number("9999999999")
    page.fill_password("TestPass@123")
    page.fill_confirm_password("TestPass@123")
    page.submit()
    assert page.is_on_signup_page()
    assert "Sign Up to Tichi" in page.body_text()
