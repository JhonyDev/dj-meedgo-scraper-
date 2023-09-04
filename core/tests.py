# from __future__ import absolute_import, unicode_literals
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
#
# from src.api.singletons import WebDriverCache
#
# url = f"https://www.1mg.com/search/all?name=oh d3"
# options = Options()
# # options.add_argument('--headless')
# driver = webdriver.Chrome(
#     executable_path='C:\\Users\\Jhony Dev\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe',
#     options=options)
# print('INSIDE SCRAPER 2')
# try:
#     driver.get(url)
# except:
#     WebDriverCache._cached_webdriver = None
#     driver = WebDriverCache.get_webdriver()
#     driver.get(url)
# print(driver)
# print('INSIDE SCRAPER 3')
# ul_tag = driver.find_elements(By.CLASS_NAME, "style__container___jkjS2")
# print(ul_tag)
# print('INSIDE SCRAPER 4')
# default_image = 'https://onemg.gumlet.io/w_150,c_fit,h_150,f_auto,q_auto/hx2gxivwmeoxxxsc1hix.png'
# for ul_ in ul_tag:
#     print('INSIDE SCRAPER 5')
#     try:
#         medicine_name = ul_.find_element(By.CLASS_NAME, "style__pro-title___3zxNC").text
#     except:
#         medicine_name = None
#     discounted_price = ul_.find_element(By.CLASS_NAME, "style__price-tag___KzOkY").text.replace(
#         '₹', '')
#     discounted_price = discounted_price.replace('MRP', '')
#     a_tag = ul_.find_element(By.TAG_NAME, "a").get_attribute('href')
#     try:
#         image_ = ul_.find_element(By.CLASS_NAME, "style__loaded___22epL").get_attribute('src')
#     except:
#         image_ = default_image
#     try:
#         original_price = ul_.find_element(By.CLASS_NAME, "style__discount-price___-Cikw").text.replace(
#             '₹', '')
#         original_price = original_price.replace('MRP', '')
#     except:
#         original_price = None
#
#     try:
#         is_available = False if ul_.find_element(By.CLASS_NAME, "style__not-available___ADBvR") else True
#     except:
#         is_available = True
#     print("SCRAPPING ONE MG FOR MEDICINES")
#     print(image_)
#     print(a_tag)
#     print(medicine_name)
#     print(discounted_price)
#     print(original_price or discounted_price)
#     print(is_available)
#     print('====' * 30)


from __future__ import absolute_import, unicode_literals

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.api.singletons import WebDriverCache

url = f"https://www.1mg.com/search/all?name=oh d3"
options = Options()
# options.add_argument('--headless')
driver = webdriver.Chrome(
    executable_path='C:\\Users\\Jhony Dev\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe',
    options=options)
print('INSIDE SCRAPER 2')
try:
    driver.get(url)
except:
    WebDriverCache._cached_webdriver = None
    driver = WebDriverCache.get_webdriver()
    driver.get(url)

if driver.find_elements(By.CLASS_NAME, "style__container___cTDz0"):
    type_ = 1
else:
    type_ = 2

if type_ == 1:
    ul_tag = driver.find_elements(By.CLASS_NAME, "style__container___cTDz0")
else:
    ul_tag = driver.find_elements(By.CLASS_NAME, "style__container___jkjS2")

default_image = 'https://onemg.gumlet.io/w_150,c_fit,h_150,f_auto,q_auto/hx2gxivwmeoxxxsc1hix.png'
for ul_ in ul_tag:
    try:
        if type_ == 1:
            medicine_name = ul_.find_element(By.CLASS_NAME, "style__pro-title___3zxNC").text
        else:
            medicine_name = ul_.find_element(By.CLASS_NAME, "style__pro-title___3G3rr").text

    except:
        medicine_name = None
    if type_ == 1:
        discounted_price = ul_.find_element(By.CLASS_NAME, "style__price-tag___B2csA").text.replace(
            '₹', '')
    else:
        discounted_price = ul_.find_element(By.CLASS_NAME, "style__price-tag___KzOkY").text.replace(
            '₹', '')
    discounted_price = discounted_price.replace('MRP', '')
    a_tag = ul_.find_element(By.TAG_NAME, "a").get_attribute('href')
    try:
        image_ = ul_.find_element(By.CLASS_NAME, "style__loaded___22epL").get_attribute('src')
    except:
        image_ = default_image
    try:
        if type_ == 1:
            original_price = ul_.find_element(By.CLASS_NAME, "style__discount-price___-Cikw").text.replace(
                '₹', '')
        else:
            original_price = ul_.find_element(By.CLASS_NAME, "style__discount-price___qlNIB").text.replace(
                '₹', '')

        original_price = original_price.replace('MRP', '')
    except:
        original_price = None

    try:
        if type_ == 1:
            is_available = False if ul_.find_element(By.CLASS_NAME, "style__not-available___ADBvR") else True
        else:
            is_available = False if ul_.find_element(By.CLASS_NAME, "style__not-available___1uGvz") else True
    except:
        is_available = True
    print("SCRAPPING ONE MG FOR MEDICINES")
    print(image_)
    print(a_tag)
    print(medicine_name)
    print(discounted_price)
    print(original_price or discounted_price)
    print(is_available)
    print('====' * 30)
