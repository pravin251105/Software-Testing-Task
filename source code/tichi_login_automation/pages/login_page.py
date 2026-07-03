"""
Page Object Model - Login Page
Tichi Web Application (Stage)
URL: https://tichi-app-webapp-stage.web.app

NOTE ON LOCATORS:
This is a live SPA (Single Page App). The locators below use robust,
attribute-based strategies (type=email, type=password, button text, etc.)
which are the most resilient to minor UI changes. Before your first run,
open the app in Chrome DevTools (F12 -> Inspect Element) and verify /
adjust the locators marked with # VERIFY if the actual DOM differs.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class LoginPage:
    URL = "https://tichi-app-webapp-stage.web.app/login"

    # ---- Locators ----
    EMAIL_INPUT = (By.XPATH, "//input[contains(translate(@aria-label,'EMAIL','email'),'email') or contains(translate(@placeholder,'EMAIL','email'),'email')]")
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(translate(normalize-space(.),'CONTINUE','continue'),'continue')]")
    PASSWORD_INPUT = (By.XPATH, "//input[contains(translate(@aria-label,'PASSWORD','password'),'password') or contains(translate(@placeholder,'PASSWORD','password'),'password')]")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(translate(normalize-space(.),'LOGIN','login'),'login')]")
    SIGNUP_LINK = (By.XPATH, "//a[contains(normalize-space(.), 'Sign Up Now')] | //button[contains(normalize-space(.), 'Sign Up Now')]")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//button[contains(translate(normalize-space(.),'FORGOT PASSWORD','forgot password'),'forgot password')] | //a[contains(translate(normalize-space(.),'FORGOT PASSWORD','forgot password'),'forgot password')]")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(@class,'error') or contains(@class,'toast') or contains(@role,'alert')]")      # VERIFY
    DASHBOARD_INDICATOR = (By.XPATH, "//a[contains(translate(normalize-space(.),'HOME','home'),'home')] | //button[contains(translate(normalize-space(.),'SEARCH','search'),'search')]")

    def __init__(self, driver, wait_timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.short_wait = WebDriverWait(driver, 5)

    def load(self):
        self.driver.get(self.URL)
        return self

    def enter_email(self, email):
        field = self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
        field.clear()
        field.send_keys(email)
        return self

    def enter_password(self, password):
        # Current login UX is a two-step flow: email -> continue -> password.
        self.click_continue_if_present()
        try:
            field = self.short_wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT))
            field.clear()
            field.send_keys(password)
        except TimeoutException:
            # For invalid/blocked flows password step may never appear.
            pass
        return self

    def click_continue_if_present(self):
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            btn.click()
        except Exception:
            # If continue is not present, the page may already be on password step.
            pass
        return self

    def click_login(self):
        try:
            btn = self.short_wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
            btn.click()
        except TimeoutException:
            # If still on step-1, trigger continue as the primary action.
            self.click_continue_if_present()
        return self

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()
        return self

    def get_password_field_type(self):
        field = self.wait.until(EC.presence_of_element_located(self.PASSWORD_INPUT))
        return field.get_attribute("type")

    def is_error_displayed(self):
        try:
            return bool(self.get_error_text())
        except Exception:
            return False

    def get_error_text(self):
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE))
            text = el.text.strip()
            if text:
                return text
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            for expected in ("Invalid login details", "Invalid email or password"):
                if expected.lower() in body_text.lower():
                    return expected
            return ""
        except Exception:
            return ""

    def is_login_successful(self):
        try:
            self.wait.until(lambda d: "/home" in d.current_url.lower() or "/dashboard" in d.current_url.lower())
            return True
        except Exception:
            try:
                self.wait.until(EC.presence_of_element_located(self.DASHBOARD_INDICATOR))
                return True
            except Exception:
                return False

    def click_signup_link(self):
        # Sign-up navigation is currently exposed from marketing/home page.
        if "/login" in self.driver.current_url.lower():
            self.driver.get("https://tichi-app-webapp-stage.web.app/")
        link = self.wait.until(EC.element_to_be_clickable(self.SIGNUP_LINK))
        link.click()
        return self

    def is_forgot_password_link_present(self):
        try:
            self.click_continue_if_present()
            self.driver.find_element(*self.FORGOT_PASSWORD_LINK)
            return True
        except Exception:
            return False

    def get_current_url(self):
        return self.driver.current_url
