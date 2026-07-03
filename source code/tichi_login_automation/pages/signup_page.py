from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class SignupPage:
    BASE_URL = "https://tichi-app-webapp-stage.web.app/sign-up"

    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    PHONE_NUMBER = (By.ID, "phoneNumber")
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    CONFIRM_PASSWORD = (By.ID, "confirmPassword")
    TERMS_CHECKBOX = (By.CSS_SELECTOR, 'input[type="checkbox"]')
    SUBMIT_BUTTON = (By.XPATH, '//button[@type="submit" and normalize-space()="Sign Up"]')

    def __init__(self, driver, wait_timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)

    def load(self, email):
        self.driver.get(f"{self.BASE_URL}?email={email}")
        return self

    def fill_first_name(self, value):
        field = self.wait.until(lambda d: d.find_element(*self.FIRST_NAME))
        field.clear()
        field.send_keys(value)
        return self

    def fill_last_name(self, value):
        field = self.wait.until(lambda d: d.find_element(*self.LAST_NAME))
        field.clear()
        field.send_keys(value)
        return self

    def fill_phone_number(self, value):
        field = self.wait.until(lambda d: d.find_element(*self.PHONE_NUMBER))
        field.clear()
        field.send_keys(value)
        return self

    def fill_password(self, value):
        field = self.wait.until(lambda d: d.find_element(*self.PASSWORD))
        field.clear()
        field.send_keys(value)
        return self

    def fill_confirm_password(self, value):
        field = self.wait.until(lambda d: d.find_element(*self.CONFIRM_PASSWORD))
        field.clear()
        field.send_keys(value)
        return self

    def accept_terms(self):
        checkbox = self.wait.until(lambda d: d.find_element(*self.TERMS_CHECKBOX))
        self.driver.execute_script("arguments[0].click();", checkbox)
        return self

    def submit(self):
        button = self.wait.until(lambda d: d.find_element(*self.SUBMIT_BUTTON))
        self.driver.execute_script("arguments[0].click();", button)
        return self

    def body_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def current_url(self):
        return self.driver.current_url

    def is_on_signup_page(self):
        return "/sign-up" in self.current_url().lower()