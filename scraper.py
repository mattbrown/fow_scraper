import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

config_webdriver = "/Users/mbrown/Downloads/chromedriver/chromedriver"
url = "http://force-of-will-tcg.wikia.com/wiki/The_Crimson_Moon%27s_Fairy_Tale_set_gallery"


class FOWScraper():
    def __init__(self):
        self.browser = None
        self.web_driver = config_webdriver

    def setup(self, url):
            os.environ["webdriver.chrome.driver"] = self.web_driver
            self.browser = webdriver.Chrome(self.web_driver)
            self.browser.get(url)

    def scrape(self):


        return [{}]

    def get_card_url_list(self):
        card_list = []

        gallery_div_id = "gallery-1"
        gallery_item_class = "wikia-gallery-item"

        gallery = self.browser.find_element_by_id(gallery_div_id)
        thumbs = gallery.find_elements_by_class_name(gallery_item_class)
        for thumb in thumbs:
            card_anchor = thumb.find_element_by_xpath("./div[2]/a")
            link = card_anchor.get_attribute("href")
            card_list.append(link)

        return card_list





    def reset(self):
        if self.browser is not None:
            self.browser.quit()
        self.browser = None



if __name__ == '__main__':
    scraper = FOWScraper()
    try:
        scraper.setup(url)
        print scraper.get_card_url_list()
    finally:
        scraper.reset()