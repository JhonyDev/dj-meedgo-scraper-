from __future__ import absolute_import, unicode_literals

import datetime

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.api.models import Medicine
from src.api.utils import get_platform_dict, NET_MEDS, PHARM_EASY, ONE_MG


# NET-MEDS

@shared_task(bind=True)
def scrape_netmeds(self, param):
    if param is None:
        return "DONE!"
    url = f"https://www.netmeds.com/catalogsearch/result/{param}/all"
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--force-device-scale-factor=0.5")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    ul_tag = driver.find_element(By.TAG_NAME, "ol")
    for li_tag in ul_tag.find_elements(By.TAG_NAME, "li"):
        category_name = li_tag.find_element(By.XPATH, ".//a[@class='category_name']")
        med_url = li_tag.find_element(By.XPATH, ".//a[@class='category_name']").get_attribute("href")
        check_med = Medicine.objects.filter(med_url=med_url).first()

        med_image = category_name.find_element(By.XPATH, ".//img[@class='product-image-photo']").get_attribute("src")
        name = li_tag.find_element(By.XPATH, ".//span[@class='clsgetname']").text
        price = li_tag.find_element(By.ID, "price").text
        price = price.replace('MRP Rs.', '')
        if check_med:
            if check_med and check_med.last_updated \
                    and check_med.last_updated > timezone.now() - datetime.timedelta(days=1):
                print("INNER LOOP! Medicine already updated today!")
                continue
            if not check_med.name or not check_med.salt_name or not check_med.price:
                update_medicine.delay(check_med.id)
                continue

        if not price:
            price = None
        try:
            is_available = not li_tag.find_element(By.CLASS_NAME, "notify_me").text
        except:
            is_available = True
        if Medicine.objects.filter(med_url=med_url).exists():
            medicine = Medicine.objects.filter(med_url=med_url).first()
            medicine.is_available = is_available
            medicine.price = medicine.price
            medicine.save()
        else:
            medicine = Medicine.objects.create(
                is_available=is_available, name=name, price=price, med_url=med_url,
                med_image=med_image, platform=get_platform_dict()[NET_MEDS])

        if name:
            update_medicine.delay(medicine.id)

    driver.quit()
    return "DONE!"


@shared_task(bind=True)
def update_medicine(self, med_pk):
    print("UPDATING MEDICINE IN NETMEDS")
    medicine = Medicine.objects.get(id=med_pk)
    if medicine.last_updated and medicine.last_updated > timezone.now() - datetime.timedelta(days=1):
        return "Medicine already updated today!"
    response = requests.get(medicine.med_url)
    soup = BeautifulSoup(response.content, "html.parser")
    drug_conf = soup.find("div", class_="drug-conf")
    salt_name = drug_conf.text.strip() if drug_conf else None
    element = soup.select_one('span.price')
    if element:
        price_strike = element.find('strike').text.strip()
        price = price_strike.split()[1]
        price = price.replace('₹', '')
        price = price.replace(',', '')
        medicine.price = price
    name = soup.find("h1", class_="black-txt")
    name = name.text.strip()
    element = soup.select_one('button[title="ADD TO CART"]')
    exists = element is not None
    medicine.salt_name = salt_name
    medicine.name = name
    medicine.is_available = exists
    medicine.last_updated = datetime.datetime.now()
    medicine.save()
    return "DONE!"


# ONE-MG

@shared_task(bind=True)
def scrape_1mg(self, param):
    if param is None:
        return "DONE!"
    url = f"https://www.1mg.com/search/all?name={param}"
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--force-device-scale-factor=0.5")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    ul_tag = driver.find_elements(By.CLASS_NAME, "style__container___cTDz0")
    default_image = 'https://onemg.gumlet.io/w_150,c_fit,h_150,f_auto,q_auto/hx2gxivwmeoxxxsc1hix.png'
    for ul_ in ul_tag:
        medicine_name = ul_.find_element(By.CLASS_NAME, "style__pro-title___3zxNC").text
        discounted_price = ul_.find_element(By.CLASS_NAME, "style__price-tag___B2csA").text.replace(
            '₹', '')
        discounted_price = discounted_price.replace('MRP', '')
        a_tag = ul_.find_element(By.TAG_NAME, "a").get_attribute('href')
        try:
            image_ = ul_.find_element(By.CLASS_NAME, "style__loaded___22epL").get_attribute('src')
        except:
            image_ = default_image
        try:
            original_price = ul_.find_element(By.CLASS_NAME, "style__discount-price___-Cikw").text.replace(
                '₹', '')
            original_price = original_price.replace('MRP', '')
        except:
            original_price = None

        try:
            is_available = True if ul_.find_element(By.CLASS_NAME, "style__not-available___ADBvR") else False
        except:
            is_available = True

        # print(image_)
        # print(a_tag)
        # print(medicine_name)
        # print(discounted_price)
        # print(original_price or discounted_price)
        # print(is_available)
        # print('====' * 30)

        if Medicine.objects.filter(med_url=a_tag).exists():
            medicine = Medicine.objects.filter(med_url=a_tag).first()
            medicine.is_available = is_available
            medicine.discounted_price = original_price or discounted_price
            medicine.price = original_price
            medicine.name = medicine_name
            medicine.save()
        else:
            medicine = Medicine.objects.create(
                is_available=is_available, name=medicine_name, discounted_price=original_price or discounted_price,
                price=original_price, med_url=a_tag,
                med_image=image_, platform=get_platform_dict()[ONE_MG])

        if medicine.name:
            update_medicine_1mg.delay(medicine.id)

    return "DONE!"


@shared_task(bind=True)
def update_medicine_1mg(self, med_pk):
    print("UPDATING MEDICINE IN ONEMG")
    medicine = Medicine.objects.get(id=med_pk)
    if medicine.last_updated and medicine.last_updated > timezone.now() - datetime.timedelta(days=1):
        return "Medicine already updated today!"
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--force-device-scale-factor=0.5")
    driver = webdriver.Chrome(options=options)
    driver.get(medicine.med_url)
    try:
        name = driver.find_element(By.CLASS_NAME, "DrugHeader__title-content___2ZaPo").text
    except:
        name = None

    try:
        salt_name = driver.find_element(By.CLASS_NAME, "DrugHeader__meta-value___vqYM0").text
    except:
        salt_name = None

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
    # print(name)
    # print(salt_name)
    # print(original_price or discounted_price)
    # print(discounted_price or original_price)
    # print(is_available)
    medicine.name = name or medicine.name
    medicine.salt_name = salt_name or medicine.salt_name
    medicine.price = original_price or medicine.price
    medicine.discounted_price = discounted_price or medicine.discounted_price
    medicine.is_available = is_available
    medicine.last_updated = datetime.datetime.now()
    medicine.save()
    return "DONE!"


# PHARM-EASY
@shared_task(bind=True)
def scrape_pharmeasy(self, param):
    if param is None:
        return "DONE!"
    base_url = 'https://pharmeasy.in'
    url = f"{base_url}/search/all?name={param}"
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
                medicine_price = menuitem.find('div', {'class': 'ProductCard_striked__jkSiD'}).text.strip()
            except:
                medicine_price = None
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
        medicine = Medicine.objects.filter(med_url=a_url).first()
        if medicine:
            medicine.is_available = is_available
            medicine.price = medicine_price
            medicine.save()
            return_list.append(medicine.pk)
            update_medicine_pharmeasy.delay(medicine.id)
            continue
        try:
            medicine = Medicine.objects.create(
                is_available=is_available, name=medicine_name, price=medicine_price, med_url=a_url,
                med_image=image_url, platform=get_platform_dict()[PHARM_EASY])
            if medicine_name:
                update_medicine_pharmeasy.delay(medicine.id)
        except Exception as e:
            print(f"MEDICINE NOT CREATED - {str(e)}")
        return_list.append(medicine.pk)
    return return_list


@shared_task(bind=True)
def update_medicine_pharmeasy(self, med_pk):
    medicine = Medicine.objects.get(id=med_pk)
    print("UPDATING MEDICINE IN PHARMEASY")
    if medicine.last_updated and medicine.last_updated > timezone.now() - datetime.timedelta(days=1):
        return "Medicine already updated today!"
    response = requests.get(medicine.med_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    firsts = soup.find_all('td', {'class': 'DescriptionTable_field__l5jJ3'})
    seconds = soup.find_all('td', {'class': 'DescriptionTable_value__0GUMC'})
    generic_name = 0
    price = None
    name = soup.find('h1', {'class': 'MedicineOverviewSection_medicineName__dHDQi'}).text.strip()
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
    salt_name = seconds[generic_name].text.strip()

    # print(name)
    # print(price or disc_price)
    # print(disc_price or price)
    # print(salt_name)
    # print(is_available)

    medicine.name = name
    medicine.price = price or disc_price
    medicine.discounted_price = disc_price or price
    medicine.salt_name = salt_name
    medicine.is_available = is_available
    medicine.last_updated = datetime.datetime.now()
    medicine.save()
    return "DONE!"
