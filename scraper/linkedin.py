from selenium.webdriver.common.by import By
from .base import BaseStrategy
from utils.parsing import extract_email, extract_phone

class LinkedInStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("linkedin", **kwargs)

    def run(self, query: str):
        out = []
        # Jobs search
        url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}"
        self.manual_login_pause(url)

        for _ in range(self.pages):
            self.gentle_scroll()
            cards = self.driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li a.result-card__full-card-link, a.base-card__full-link")
            if not cards:
                cards = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")

            links = []
            for a in cards:
                href = a.get_attribute("href")
                if href and "/jobs/view/" in href:
                    links.append(href)
            links = list(dict.fromkeys(links))  # de-dup

            for link in links:
                try:
                    self.driver.execute_script("window.open(arguments[0], '_blank');", link)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    try:
                        self.gentle_scroll()
                        # job title
                        try:
                            title = self.driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
                        except Exception:
                            title = "LinkedIn Job"

                        # company
                        try:
                            company = self.driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, span.topcard__flavor").text.strip()
                        except Exception:
                            company = ""

                        name = f"{title} @ {company}".strip(" @")

                        # Try to find any contact info in description
                        try:
                            desc = self.driver.find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup").text
                        except Exception:
                            desc = self.driver.page_source
                        email = extract_email(desc)
                        phone = extract_phone(desc)

                        out.append(self.row(name=name, email=email, phone=phone, website="", source_url=link))
                    finally:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                except Exception:
                    continue

            # Try a next button if available
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                if next_btn.is_enabled():
                    next_btn.click()
                else:
                    break
            except Exception:
                break

        return out
