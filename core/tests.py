import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Initialize the webdriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# Open the URL
driver.get("https://healthplus.flipkart.com/")

# Wait until the qck-list-item divs appear
wait = WebDriverWait(driver, 10000)

input_ = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "src-front")))

# Find the input field by class name
input_field = driver.find_element(By.CLASS_NAME, "src-front")

# Input text into the field
input_field.send_keys("pana")

divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "qck-list-item")))

# Loop through each div
for div in divs:
    # Extract the necessary information
    brand_name = div.find_element_by_class_name("brand-name").text
    highlighted_text = div.find_element_by_css_selector("a.text-highlighted").text
    o_price = div.find_element_by_class_name("o-price").text
    s_price = div.find_element_by_class_name("s-price").text

    # Check if js_add_to_cart link exists
    add_to_cart_link = div.find_elements_by_css_selector("a.js_add_to_cart")
    if add_to_cart_link:
        has_add_to_cart = True
    else:
        has_add_to_cart = False

    # Print the extracted information and whether the add_to_cart link exists
    print("Brand name: ", brand_name)
    print("Highlighted text: ", highlighted_text)
    print("Original price: ", o_price)
    print("Sale price: ", s_price)
    print("Has add to cart: ", has_add_to_cart)
    print()

# Close the webdriver
driver.quit()
