# import requests
# from bs4 import BeautifulSoup
#
# # response = requests.get("https://pharmeasy.in/online-medicine-order/petril-md-0-25mg-tablet-19806")
# # response = requests.get("https://pharmeasy.in/online-medicine-order/somo-strip-of-15-tablets-2987708")
# response = requests.get("https://pharmeasy.in/online-medicine-order/sumo-strip-of-15-tablets-2709")
# soup = BeautifulSoup(response.text, 'html.parser')
# firsts = soup.find_all('td', {'class': 'DescriptionTable_field__l5jJ3'})
# seconds = soup.find_all('td', {'class': 'DescriptionTable_value__0GUMC'})
# generic_name = 0
# price = None
# name = soup.find('h1', {'class': 'MedicineOverviewSection_medicineName__dHDQi'}).text.strip()
# try:
#     price = soup.find('div', {'class': 'PriceInfo_ourPrice__jFYXr'}).text.strip()
# except:
#     try:
#         price = soup.find('span', {'class': 'PriceInfo_striked__Hk2U_'}).text.strip()
#     except:
#         pass
# if price:
#     price = price.replace('MRP', '')
#     price = price.replace('*', '')
#     price = price.replace('₹', '')
#     price = float(price)
#
# disc_price = None
# try:
#     disc_price = soup.find('div', class_='PriceInfo_gcdDiscountContainer__hr0YD').find('span').text
#     if disc_price:
#         disc_price = disc_price.replace('MRP', '')
#         disc_price = disc_price.replace('*', '')
#         disc_price = disc_price.replace('₹', '')
#         disc_price = float(disc_price)
# except:
#     pass
#
# for first in firsts:
#     if first.text.strip() == 'Contains':
#         break
#     generic_name += 1
# is_available = True if price or disc_price else False
# salt_name = seconds[generic_name].text.strip()
#
# print(name)
# print(price or disc_price)
# print(disc_price or price)
# print(salt_name)
# print(is_available)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
# options.add_argument('--headless')
# options.add_argument("--force-device-scale-factor=0.5")
driver = webdriver.Chrome(options=options)
driver.get("https://www.1mg.com/drugs/famomeg-40mg-tablet-648333")
name = driver.find_element(By.CLASS_NAME, "DrugHeader__title-content___2ZaPo").text
salt_name = driver.find_element(By.CLASS_NAME, "DrugHeader__meta-value___vqYM0").text
print(name)
print(salt_name)
try:
    original_price = driver.find_element(By.CLASS_NAME, "DrugPriceBox__slashed-price___2UGqd").text.replace(
        '₹', '')
except:
    original_price = None
try:
    discounted_price = driver.find_element(By.CLASS_NAME,
                                           "DrugPriceBox__price___dj2lv").text.replace(
        '₹', '')
except:
    discounted_price = None
is_available = True if original_price or discounted_price else False
print(name)
print(salt_name)
print(original_price or discounted_price)
print(discounted_price or original_price)
print(is_available)
