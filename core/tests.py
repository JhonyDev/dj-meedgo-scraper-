from __future__ import absolute_import, unicode_literals

from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument('--headless')
# options.add_argument("--force-device-scale-factor=0.5")
response = requests.get("medicine.med_url")
soup = BeautifulSoup(response.content, "html.parser")
drug_conf = soup.find("div", class_="drug-conf")
salt_name = drug_conf.text.strip() if drug_conf else None
element = soup.select_one('span.price')
price = None
if element:
    price_strike = element.find('strike').text.strip()
    price = price_strike.split()[1]
    price = price.replace('₹', '')
    price = price.replace(',', '')
    price = float(price)

disc_element = soup.select_one('span.final-price')
discounted_price = None
if disc_element:
    price_strike = disc_element.text.strip()
    discounted_price = price_strike.replace('₹', '')
    discounted_price = discounted_price.replace(',', '')
    discounted_price = discounted_price.replace('Best Price*  ', '')
    discounted_price = discounted_price.replace('*', '')
    discounted_price = discounted_price.replace('Best', '')
    discounted_price = discounted_price.replace('Price', '')
    discounted_price = discounted_price.replace('MRP', '')
    discounted_price = discounted_price.replace(' ', '')
    discounted_price = float(discounted_price)
name = soup.find("h1", class_="black-txt")
name = name.text.strip()
element = soup.select_one('button[title="ADD TO CART"]')
is_available = element is not None

print(name)
print(salt_name)
print(price)
print(discounted_price)
print(is_available)
sleep(1000)
