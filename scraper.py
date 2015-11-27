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
            card_anchor_list = thumb.find_elements_by_xpath("./div[2]/a")
            for anchor in card_anchor_list:
                link = anchor.get_attribute("href")
                card_list.append(link)

        return card_list

    def get_card_info(self, url):
        card_info = {
            'name': None,
            'attribute': None,
            'card_type': None,
            'race': None,
            'abilities': None,
            'flavor': None,
            'cluster': None,
            'set': None,
            'rarity': None,
            'id': None
        }

        self.browser.get(url)
        table = self.browser.find_elements_by_xpath('//*[@id="mw-content-text"]/table')[-1]

        #Get Name
        name = table.find_element_by_xpath('./tbody/tr[1]/th').text
        card_info['name'] = name

        #Get attribute
        attribute = table.find_element_by_xpath('./tbody/tr[3]/td[2]/a[1]').text
        card_info['attribute'] = attribute

        #Get card_type
        card_type = table.find_element_by_xpath('./tbody/tr[4]/td[2]/a[1]').text
        card_info['card_type'] = card_type

        #Get race
        race = table.find_element_by_xpath('./tbody/tr[5]/td[2]/a[1]').text
        card_info['race'] = race

        #get abilities
        abilities = table.find_element_by_xpath('./tbody/tr[5]/td[2]').text
        card_info['abilities'] = abilities

        #get flavor
        flavor = table.find_element_by_xpath('./tbody/tr[6]/td[2]').text
        card_info['flavor'] = flavor

        raw_set_data = table.find_element_by_xpath('./tbody/tr[9]/td')
        self.parse_set_and_rarity(card_info, raw_set_data)

        return card_info

    def parse_set_and_rarity(self, card_info, raw_set_data):
        #get cluster
        cluster = raw_set_data.find_element_by_xpath('./b').text
        card_info['cluster'] = cluster

        #get set
        set = raw_set_data.find_element_by_xpath('./a').text
        card_info['set'] = set

        text_set_data = raw_set_data.text
        id_and_rarity_parts = text_set_data.split('\n')[-1].split(' ')

        #get rarity
        rarity = id_and_rarity_parts[-1].replace(')', '')
        card_info['rarity'] = rarity

        #get id
        id = id_and_rarity_parts[0].replace('(', '')
        card_info['id'] = id

    def reset(self):
        if self.browser is not None:
            self.browser.quit()
        self.browser = None



if __name__ == '__main__':
    card_url = "http://force-of-will-tcg.wikia.com/wiki/Grimm,_the_Fairy_Tale_Prince"

    scraper = FOWScraper()
    try:
        scraper.setup(url)
        print scraper.get_card_info(card_url)
    finally:
        scraper.reset()