from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base import BaseStrategy
from utils.parsing import extract_email, extract_phone

class JustDialStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("justdial", **kwargs)

    def search_url(self, query: str):
        q = query.replace(" ", "-")
        city = (self.city or "Mumbai").replace(" ", "-")
        return f"https://www.justdial.com/{city}/{q}"

    def run(self, query: str):
        out = []
        self.manual_login_pause(self.search_url(query))

        # Allow JS to populate
        time.sleep(4)
        self.gentle_scroll()
        time.sleep(2)

        for page in range(1, self.pages + 1):
            if page > 1:
                self.driver.get(self.search_url(query) + f"/page-{page}")
                time.sleep(4)
                self.gentle_scroll()

            cards = self.driver.find_elements(By.CSS_SELECTOR, "div.jsx-1614333167.cardbox, li.cntanr")
            if not cards:
                cards = self.driver.find_elements(By.CSS_SELECTOR, "div.business-card")

            for c in cards:
                try:
                    name = email = phone = website = source_url = ""

                    # Name
                    try:
                        name_el = c.find_element(By.CSS_SELECTOR, "a[title], a.business-name, h2 a")
                        name = name_el.text.strip()
                        source_url = name_el.get_attribute("href") or ""
                    except Exception:
                        pass

                    # Click Call button if hidden
                    try:
                        call_btn = c.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
                        phone = call_btn.get_attribute("href").replace("tel:", "").strip()
                    except NoSuchElementException:
                        # Sometimes hidden behind click
                        try:
                            btn = c.find_element(By.CSS_SELECTOR, "span:contains('Call Now'), button:contains('Call Now')")
                            btn.click()
                            time.sleep(1)
                            phone = extract_phone(c.get_attribute("innerText"))
                        except Exception:
                            phone = extract_phone(c.get_attribute("innerText"))

                    # Website (on details page)
                    if source_url:
                        self.driver.execute_script("window.open(arguments[0], '_blank');", source_url)
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        try:
                            time.sleep(3)
                            self.gentle_scroll()
                            try:
                                w = self.driver.find_element(By.CSS_SELECTOR, "a[href^='http']:not([href*='justdial'])")
                                website = w.get_attribute("href")
                            except Exception:
                                website = ""
                            email = extract_email(self.driver.page_source)
                        finally:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])

                    out.append(self.row(name, email, phone, website, source_url))
                except Exception:
                    continue

        return out
