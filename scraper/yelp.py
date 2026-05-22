from selenium.webdriver.common.by import By
from .base import BaseStrategy
from utils.parsing import extract_email, extract_phone
import time

class YelpStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("yelp", **kwargs)

    def run(self, query: str):
        out = []
        loc = self.location or "New York"
        url = f"https://www.yelp.com/search?find_desc={query.replace(' ', '+')}&find_loc={loc.replace(' ', '+')}"
        self.manual_login_pause(url)
        time.sleep(3)
        self.gentle_scroll()

        for page in range(self.pages):
            if page > 0:
                self.driver.get(url + f"&start={page*10}")
                time.sleep(3)
                self.gentle_scroll()

            cards = self.driver.find_elements(By.XPATH, "//h3//a[contains(@href,'/biz/')]")
            links = [a.get_attribute("href") for a in cards if a.get_attribute("href")]
            links = list(dict.fromkeys(links))

            for link in links:
                try:
                    self.driver.execute_script("window.open(arguments[0], '_blank');", link)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(3)
                    self.gentle_scroll()

                    try:
                        name = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
                    except Exception:
                        name = "Yelp Business"

                    # Visible body text only
                    body_text = self.driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")

                    phone = extract_phone(body_text)
                    email = extract_email(body_text)

                    try:
                        website_el = self.driver.find_element(By.XPATH, "//a[contains(@href,'http') and contains(text(),'Website')]")
                        website = website_el.get_attribute("href")
                    except Exception:
                        website = ""

                    out.append(self.row(name, email, phone, website, link))
                except Exception:
                    pass
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
        return out
