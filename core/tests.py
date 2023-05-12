# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
#
# #
# # url = f"https://www.1mg.com/search/all?name=Petril MD"
# # options = Options()
# # options.add_argument('--headless')
# # options.add_argument("--force-device-scale-factor=0.5")
# # driver = webdriver.Chrome(options=options)
# # driver.get(url)
# # ul_tag = driver.find_elements(By.CLASS_NAME, "style__container___cTDz0")
# # default_image = 'https://onemg.gumlet.io/w_150,c_fit,h_150,f_auto,q_auto/hx2gxivwmeoxxxsc1hix.png'
# # for ul_ in ul_tag:
# #     medicine_name = ul_.find_element(By.CLASS_NAME, "style__pro-title___3zxNC").text
# #     discounted_price = ul_.find_element(By.CLASS_NAME, "style__price-tag___B2csA").text
# #     a_tag = ul_.find_element(By.TAG_NAME, "a").get_attribute('href')
# #     try:
# #         image_ = ul_.find_element(By.CLASS_NAME, "style__loaded___22epL").get_attribute('src')
# #     except:
# #         image_ = default_image
# #     try:
# #         original_price = ul_.find_element(By.CLASS_NAME, "style__discount-price___-Cikw").text
# #     except:
# #         original_price = None
# #
# #     try:
# #         is_available = True if ul_.find_element(By.CLASS_NAME, "style__not-available___ADBvR") else False
# #     except:
# #         is_available = True
# #     print(image_)
# #     print(a_tag)
# #     print(medicine_name)
# #     print(discounted_price)
# #     print(original_price or discounted_price)
# #     print(is_available)
# #     print('====' * 30)
# #
# url = f"https://www.1mg.com/drugs/petril-md-0.5-tablet-57666"
# options = Options()
# options.add_argument('--headless')
# options.add_argument("--force-device-scale-factor=0.5")
# driver = webdriver.Chrome(options=options)
# driver.get(url)
# name = driver.find_element(By.CLASS_NAME, "DrugHeader__title-content___2ZaPo").text
# salt_name = driver.find_element(By.CLASS_NAME, "DrugHeader__meta-value___vqYM0").text
# try:
#     original_price = driver.find_element(By.CLASS_NAME, "PriceBoxPlanOption__stike___pDQVN").text.replace(
#         '₹', '')
#     discounted_price = driver.find_element(By.CLASS_NAME, "PriceBoxPlanOption__offer-price-cp___2QPU_").text.replace(
#         '₹', '')
#     is_available = True
# except:
#     is_available = False
#     discounted_price = None
#     original_price = None
# print(name)
# print(salt_name)
# print(original_price)
# print(discounted_price)
# print(is_available)


import re

# sample string
string_with_numbers = "MRP105"

# extract only numbers using regular expressions
numbers = re.findall('\d+', string_with_numbers)

# print the extracted numbers
print(numbers)
