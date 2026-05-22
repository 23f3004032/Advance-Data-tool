import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def make_driver(profile_dir: str, headless: bool = False, implicit_wait: int = 5):
    options = Options()
    # Persist login sessions per site
    options.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Selenium Manager auto-installs chromedriver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(implicit_wait)
    return driver
