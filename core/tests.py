# from __future__ import absolute_import, unicode_literals
#
# import time
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
#
# param = 'pana'
# url = f"https://pharmeasy.in/search/all?name={param}"
# options = Options()
# # options.add_argument('--headless')
# # options.add_argument("--force-device-scale-factor=0.5")
# driver = webdriver.Chrome(options=options)
# driver.get(url)
# parent_div = driver.find_element(By.CLASS_NAME, 'Search_fullWidthLHS__mteti')
# menuitems = driver.find_elements(By.CSS_SELECTOR, 'div[role="menuitem"]')
# for menuitem in menuitems:
#     medicine_name = menuitem.find_element(By.CLASS_NAME, 'ProductCard_medicineName__8Ydfq').text
#     try:
#         medicine_price = menuitem.find_element(By.CLASS_NAME, 'ProductCard_ourPrice__yDytt').text
#     except:
#         try:
#             medicine_price = menuitem.find_element(By.CLASS_NAME, 'ProductCard_striked__jkSiD').text
#         except:
#             medicine_price = None
#     div_element = menuitem.find_element(By.CLASS_NAME, 'ProductCard_productWarningAndCta__kKe3q')
#     is_available = False
#     if "Out of Stock" not in div_element.text:
#         is_available = True
#     if medicine_price:
#         medicine_price = medicine_price.replace('*', '')
#         medicine_price = medicine_price.replace('₹', '')
#
#     product_image = menuitem.find_element(By.CLASS_NAME, "ProductCard_productImage__dq5lq")
#     image_url = product_image.get_attribute("src")
#     print(product_image.get_attribute('outerHTML'))
#     print(image_url)
#     print(medicine_name)
#     print(medicine_price)
#     print(is_available)
#     print('---' * 20)
#
# time.sleep(100)
# driver.quit()
import requests
from bs4 import BeautifulSoup

url = f"https://pharmeasy.in/online-medicine-order/panadol-tab-57196"

# menuitems = parent_div.find_all('div', {'role': 'menuitem'})
# for menuitem in menuitems:
#     medicine_name = menuitem.find('h1', {'class': 'ProductCard_medicineName__8Ydfq'}).text.strip()
#     try:
#         medicine_price = menuitem.find('div', {'class': 'ProductCard_ourPrice__yDytt'}).text.strip()
#     except:
#         try:
#             medicine_price = menuitem.find('div', {'class': 'ProductCard_striked__jkSiD'}).text.strip()
#         except:
#             medicine_price = None
#     div_element = menuitem.find('div', {'class': 'ProductCard_productWarningAndCta__kKe3q'})
#     is_available = False
#     if "Out of Stock" not in div_element.text:
#         is_available = True
#     noscript_tag = menuitem.find("noscript")
#     img_tag = noscript_tag.find("img", {"class": "ProductCard_productImage__dq5lq"})
#     image_url = img_tag.get('src')
#     a_tag = menuitem.find("a", {"class": "ProductCard_defaultWrapper__nxV0R"})
#     a_url = f"{base_url}{a_tag.get('href')}"
#     print(a_url)
#     print(image_url)
#     print(medicine_name)
#     print(medicine_price)
#     print(is_available)
#     print('---' * 20)
