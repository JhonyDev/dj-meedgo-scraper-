from __future__ import absolute_import, unicode_literals

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless')
options.add_argument("--force-device-scale-factor=0.5")
driver = webdriver.Chrome(options=options)
driver.get("https://www.1mg.com/drugs/dolobest-od-200mg-tablet-296339")
try:
    name = driver.find_element(By.CLASS_NAME, "DrugHeader__title-content___2ZaPo").text
except:
    name = None

try:
    salt_name = driver.find_element(By.CSS_SELECTOR, '.saltInfo.DrugHeader__meta-value___vqYM0').text
except:
    salt_name = None

try:
    original_price = driver.find_element(By.CLASS_NAME, "DrugPriceBox__slashed-price___2UGqd").text.replace(
        '₹', '')
except:
    try:
        original_price = driver.find_element(By.CLASS_NAME, "PriceBoxPlanOption__stike___pDQVN").text.replace(
            '₹', '')
    except:
        original_price = None
try:
    discounted_price = driver.find_element(By.CLASS_NAME,
                                           "DrugPriceBox__price___dj2lv").text.replace(
        '₹', '')
except:
    try:
        discounted_price = driver.find_element(By.CLASS_NAME,
                                               "PriceBoxPlanOption__offer-price-cp___2QPU_").text.replace(
            '₹', '')
    except:
        discounted_price = None
is_available = True if original_price or discounted_price else False

print(name)
print(salt_name)
print(original_price or discounted_price)
print(discounted_price or original_price)
print(is_available)
