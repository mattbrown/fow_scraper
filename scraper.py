import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

config_webdriver = "/Users/mbrown/Downloads/chromedriver/chromedriver"
url = "http://force-of-will-tcg.wikia.com/wiki/The_Crimson_Moon%27s_Fairy_Tale"


class FOWScraper():
    def __init__(self):
        self.browser = None
        self.web_driver = config_webdriver

    def setup(self, url):
            os.environ["webdriver.chrome.driver"] = self.web_driver
            self.browser = webdriver.Chrome(self.web_driver)
            self.browser.get(url)

    def reset(self, url):
        if self.browser is not None:
            self.browser.quit()
        self.browser = None



if __name__ == '__main__':
    scraper = FOWScraper()
    scraper.setup(url)