import os
from selenium import webdriver
import urllib
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

webdriver_path = "/Users/mbrown/Downloads/chromedriver/"
config_webdriver = webdriver_path + "chromedriver"
abp_extension = webdriver_path + "Adblock-Plus_v1.9.4.crx"
output_file_name = 'fow_grim_alice1.csv'

url_list = [
    # "http://force-of-will-tcg.wikia.com/wiki/The_Crimson_Moon%27s_Fairy_Tale_set_gallery",
    # "http://force-of-will-tcg.wikia.com/wiki/The_Castle_of_Heaven_and_The_Two_Towers_set_gallery",
    # "http://force-of-will-tcg.wikia.com/wiki/The_Moon_Priestess_Returns_set_gallery",
    # "http://force-of-will-tcg.wikia.com/wiki/The_Millennia_of_Ages_set_gallery",
    # "http://force-of-will-tcg.wikia.com/wiki/Vingolf:_Engage_Knights_set_gallery",
    "http://force-of-will-tcg.wikia.com/wiki/The_Seven_Kings_of_the_Lands_set_gallery",
]


class FOWScraper():
    def __init__(self):
        self.browser = None
        self.web_driver = config_webdriver

    def setup(self, url):
        os.environ["webdriver.chrome.driver"] = self.web_driver
        options = webdriver.ChromeOptions()
        options.add_extension(abp_extension)
        self.browser = webdriver.Chrome(self.web_driver, chrome_options=options)
        self.browser.get(url)

    def scrape(self):
        card_list = self.get_card_url_list()
        card_info_list = []
        for card_url in card_list:
            card_info = self.smart_parse(card_url)
            card_info_list.append(card_info)

        self.output_to_csv(card_info_list)

        return card_info_list

    def output_to_csv(self, card_info_list):
        keys = card_info_list[0].keys()
        output_file_name = card_info_list[0]['set'] + ".csv"
        with open(output_file_name, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(card_info_list)

    def get_card_url_list(self):
        print "getting card list..."
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

    def smart_parse(self, url):
        print "getting smart card info for %s" % url
        card_info = {
            'name': None,
            'attribute': None,
            'card_type': None,
            'race': None,
            'cost': None,
            'attack': None,
            'defense': None,
            'abilities': None,
            'flavor': None,
            'cluster': None,
            'set': None,
            'rarity': None,
            'id': None,
            'wiki_link': url
        }

        self.browser.get(url)
        table = self.browser.find_elements_by_xpath('//*[@id="mw-content-text"]/table')[-1]

        #Get Name
        name = table.find_element_by_xpath('./tbody/tr[1]/th').text
        card_info['name'] = name

        row_list = table.find_elements_by_xpath('./tbody/tr')
        for row in row_list:
            columns = row.find_elements_by_xpath('./td')
            self.parse_table_row(card_info, columns)

        raw_set_and_rarity = row_list[-1].find_element_by_xpath('./td')
        self.parse_set_and_rarity(card_info, raw_set_and_rarity)

        self.save_image_detail(card_info, table)

        return card_info

    def parse_table_row(self, card_info, columns):
        if len(columns) < 2:
            return

        column_label = columns[0].text
        card_data = columns[1].text.encode("utf-8")

        if column_label == "Attribute:":
            card_info['attribute'] = card_data
        elif column_label == "Card Type:":
            card_info['card_type'] = card_data
        elif column_label == "Race:":
            card_info['race'] = card_data
        elif column_label == "Cost:":
            card_info['cost'] = self.parse_cost(columns[1])
        elif column_label == "ATK/DEF:":
            atk_def = card_data.split('/')
            atk = atk_def[0]
            defense = atk_def[1]
            card_info['attack'] = atk
            card_info['defense'] = defense
        elif column_label == "Abilities:":
            card_info['abilities'] = card_data
        elif column_label == "Flavor Text:":
            card_info['flavor'] = card_data
        else:
            print "UNUSED ROW: " + column_label

    def parse_cost(self, cost_column):
        cost = []
        for imgs in cost_column.find_elements_by_xpath('./a/img'):
            alt_data = imgs.get_attribute("alt")
            cost.append(alt_data)
        return cost

    @staticmethod
    def parse_set_and_rarity(card_info, raw_set_data):
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

    @staticmethod
    def save_image_detail(card_info, web_table):
        img_src = web_table.find_element_by_xpath('./tbody/tr[2]/td/div/a/img').get_attribute('src')
        scale_index = img_src.find('/scale-to-width')
        img_src = img_src[:scale_index]
        directory_path = "fow_images/" + card_info['cluster'] + "/" + card_info['set']
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        file_name = card_info['id'].replace('/', '-')
        file_path = directory_path + "/" + file_name + ".jpg"

        urllib.urlretrieve(img_src, file_path)

        card_info['image_path'] = file_path

    def reset(self):
        if self.browser is not None:
            self.browser.quit()
        self.browser = None



if __name__ == '__main__':
    scraper = FOWScraper()
    card_url = "http://force-of-will-tcg.wikia.com/wiki/Aesop,_the_Prince%27s_Tutor"
    try:
        for set_url in url_list:
            scraper.setup(set_url)
            scraper.scrape()
        # card_data =  scraper.smart_parse(card_url)
        # print card_data
        # scraper.output_to_csv([card_data])
    finally:
        # pass
        scraper.reset()