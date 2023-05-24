from __future__ import absolute_import, unicode_literals

import urllib.parse
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

input_string = "Janumet 50/1000mg Tablet 15'S"
encoded_string = urllib.parse.quote(input_string)
encoded_string = encoded_string.replace('/', '')
print(encoded_string)

url = f"https://www.netmeds.com/catalogsearch/result/{encoded_string}/all"

options = Options()
# options.add_argument('--headless')
# options.add_argument("--force-device-scale-factor=0.5")
driver = webdriver.Chrome(options=options)
driver.get(url)
ul_tag = driver.find_element(By.TAG_NAME, "ol")
for li_tag in ul_tag.find_elements(By.TAG_NAME, "li"):
    category_name = li_tag.find_element(By.XPATH, ".//a[@class='category_name']")
    med_url = li_tag.find_element(By.XPATH, ".//a[@class='category_name']").get_attribute("href")

    med_image = category_name.find_element(By.XPATH, ".//img[@class='product-image-photo']").get_attribute("src")
    name = li_tag.find_element(By.XPATH, ".//span[@class='clsgetname']").text
    price = li_tag.find_element(By.ID, "price").text
    price = price.replace('MRP Rs.', '')

    if not price:
        price = None
    try:
        is_available = not li_tag.find_element(By.CLASS_NAME, "notify_me").text
    except:
        is_available = True

    discounted_price = li_tag.find_element(By.ID, "final_price").text
    discounted_price = discounted_price.replace('MRP Rs.', '')
    discounted_price = discounted_price.replace('₹', '')
    if not discounted_price:
        discounted_price = None
    print(med_url)
    print(med_image)
    print(name)
    print(price)
    print(discounted_price)
    print(is_available)
