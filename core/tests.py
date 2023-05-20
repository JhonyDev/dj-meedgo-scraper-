import requests
from bs4 import BeautifulSoup

base_url = ''
url = f"https://pharmeasy.in/search/all?name=pana"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
parent_div = soup.find('div', {'class': 'Search_fullWidthLHS__mteti'})
menuitems = parent_div.find_all('div', {'role': 'menuitem'})
return_list = []
for menuitem in menuitems:
    try:
        medicine_name = menuitem.find('h1', {'class': 'ProductCard_medicineName__8Ydfq'}).text.strip()
    except:
        continue
    try:
        medicine_price = menuitem.find('div', {'class': 'ProductCard_ourPrice__yDytt'}).text.strip()
    except:
        try:
            medicine_price = menuitem.find('span', {'class': 'ProductCard_striked__jkSiD'}).text.strip()
        except:
            medicine_price = None

    try:
        disc_price = menuitem.find('div', {'class': 'ProductCard_gcdDiscountContainer__CCi51'}).find(
            'span').text.strip()
    except:
        disc_price = None
    div_element = menuitem.find('div', {'class': 'ProductCard_productWarningAndCta__kKe3q'})
    is_available = False
    if "Out of Stock" not in div_element.text:
        is_available = True
    noscript_tag = menuitem.find("noscript")
    img_tag = noscript_tag.find("img", {"class": "ProductCard_productImage__dq5lq"})
    image_url = img_tag.get('src')
    a_tag = menuitem.find("a", {"class": "ProductCard_defaultWrapper__nxV0R"})
    a_url = f"{base_url}{a_tag.get('href')}"
    try:
        medicine_price = medicine_price.replace('MRP ₹', '')
    except:
        pass
    try:
        medicine_price = medicine_price.replace('*', '')
    except:
        pass
    if medicine_price:
        medicine_price = medicine_price.replace('₹', '')

    if disc_price:
        disc_price = disc_price.replace('₹', '')
        disc_price = disc_price.replace('*', '')
        disc_price = disc_price.replace('MRP', '')
        disc_price = float(disc_price)

    print(image_url)
    print(medicine_name)
    print(medicine_price)
    print(disc_price)
    print(is_available)
