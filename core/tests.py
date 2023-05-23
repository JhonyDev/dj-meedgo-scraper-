from __future__ import absolute_import, unicode_literals

import requests
from bs4 import BeautifulSoup

response = requests.get(
    "https://pharmeasy.in/health-care/products/glucon-d-nimbu-paani-health-food-box-of-450-g-231386")
soup = BeautifulSoup(response.text, 'html.parser')
firsts = soup.find_all('td', {'class': 'DescriptionTable_field__l5jJ3'})
seconds = soup.find_all('td', {'class': 'DescriptionTable_value__0GUMC'})
generic_name = 0
price = None
try:
    name = soup.find('h1', {'class': 'MedicineOverviewSection_medicineName__dHDQi'}).text.strip()
except:
    name = None
try:
    price = soup.find('div', {'class': 'PriceInfo_ourPrice__jFYXr'}).text.strip()
except:
    try:
        price = soup.find('span', {'class': 'PriceInfo_striked__Hk2U_'}).text.strip()
    except:
        pass
if price:
    price = price.replace('MRP', '')
    price = price.replace('*', '')
    price = price.replace('₹', '')
    price = float(price)

disc_price = None
try:
    disc_price = soup.find('div', class_='PriceInfo_gcdDiscountContainer__hr0YD').find('span').text
    if disc_price:
        disc_price = disc_price.replace('MRP', '')
        disc_price = disc_price.replace('*', '')
        disc_price = disc_price.replace('₹', '')
        disc_price = float(disc_price)
except:
    pass

for first in firsts:
    if first.text.strip() == 'Contains':
        break
    generic_name += 1
is_available = True if price or disc_price else False
try:
    salt_name = firsts[generic_name].text.strip()
except:
    salt_name = None
print(name)
print(price or disc_price)
print(disc_price or price)
print(salt_name)
print(is_available)
