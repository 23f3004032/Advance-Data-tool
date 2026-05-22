import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.browser import make_driver
from utils.parsing import extract_email, extract_phone, clean_url, na
from dotenv import load_dotenv

load_dotenv()

class BaseStrategy:
    def __init__(self, site_key: str, headless=False, login_wait=45, pages=1, city=None, location=None):
        self.site_key = site_key
        self.headless = headless
        self.login_wait = int(login_wait)
        self.pages = int(pages)
        self.city = city
        self.location = location
        implicit = int(os.getenv("IMPLICIT_WAIT", "5"))
        self.wait_seconds = int(os.getenv("EXPLICIT_WAIT", "15"))
        self.driver = make_driver(profile_dir=f"profiles/{site_key}", headless=headless, implicit_wait=implicit)

    def wait_visible(self, by, selector):
        return WebDriverWait(self.driver, self.wait_seconds).until(
            EC.visibility_of_element_located((by, selector))
        )

    def wait_all_present(self, by, selector):
        return WebDriverWait(self.driver, self.wait_seconds).until(
            EC.presence_of_all_elements_located((by, selector))
        )

    def gentle_scroll(self):
        for _ in range(5):
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(0.7)

    def manual_login_pause(self, url):
        self.driver.get(url)
        # Give the user time to login if needed
        time.sleep(self.login_wait)

    def run(self, query: str):
        """Override in subclass. Must return list of dicts: name, email, phone, website, source_url"""
        raise NotImplementedError

    def teardown(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    # Common normalizer
    def row(self, name=None, email=None, phone=None, website=None, source_url=None):
        return {
            "name": na(name),
            "email": na(email),
            "phone": na(phone),
            "website": na(clean_url(website)),
            "source_url": na(clean_url(source_url)),
        }
