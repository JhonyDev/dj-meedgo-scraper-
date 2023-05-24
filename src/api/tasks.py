from __future__ import absolute_import, unicode_literals

import datetime
import urllib.parse

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.api.models import Medicine
from src.api.utils import get_platform_dict, NET_MEDS, PHARM_EASY, ONE_MG

# NET-MEDS
limit_threading = False


@shared_task(bind=True)
def scrape_netmeds(self, param):
    print("SEARCHING IN NETMEDS")
    if param is None:
        return "DONE!"
    param = urllib.parse.quote(param)
    param = param.replace('/', '')
    url = f"https://www.netmeds.com/catalogsearch/result/{param}/all"
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--force-device-scale-factor=0.5")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "ol")))
    ul_tag = driver.find_element(By.TAG_NAME, "ol")
    for li_tag in ul_tag.find_elements(By.TAG_NAME, "li"):
        category_name = li_tag.find_element(By.XPATH, ".//a[@class='category_name']")
        med_url = li_tag.find_element(By.XPATH, ".//a[@class='category_name']").get_attribute("href")
        check_med = Medicine.objects.filter(med_url=med_url).first()

        med_image = category_name.find_element(By.XPATH, ".//img[@class='product-image-photo']").get_attribute("src")
        name = li_tag.find_element(By.XPATH, ".//span[@class='clsgetname']").text
        price = li_tag.find_element(By.ID, "price").text
        price = price.replace('MRP Rs.', '')
        if limit_threading:
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

        if Medicine.objects.filter(med_url=med_url).exists():
            medicine = Medicine.objects.filter(med_url=med_url).first()
            medicine.is_available = is_available
            medicine.price = price or medicine.price
            medicine.discounted_price = discounted_price or medicine.discounted_price
            medicine.save()
        else:
            medicine = Medicine.objects.create(
                is_available=is_available, name=name, price=price, discounted_price=discounted_price, med_url=med_url,
                med_image=med_image, platform=get_platform_dict()[NET_MEDS])
        if name:
            update_medicine.delay(medicine.id)

    driver.quit()
    return "DONE!"


@shared_task(bind=True)
def update_medicine(self, med_pk):
    print("UPDATING MEDICINE IN NETMEDS")
    medicine = Medicine.objects.get(id=med_pk)
    if limit_threading:
        if medicine.last_updated and medicine.last_updated > timezone.now() - datetime.timedelta(days=1):
            return "Medicine already updated today!"
    response = requests.get(medicine.med_url)
    soup = BeautifulSoup(response.content, "html.parser")
    drug_conf = soup.find("div", class_="drug-conf")
    salt_name = drug_conf.text.strip() if drug_conf else None
    element = soup.select_one('span.price')
    price = None
    if element:
        price_strike = element.find('strike').text.strip()
        price = price_strike.split()[1]
        price = price.replace('₹', '')
        price = price.replace(',', '')
        price = float(price)

    disc_element = soup.select_one('span.final-price')
    discounted_price = None
    if disc_element:
        price_strike = disc_element.text.strip()
        discounted_price = price_strike.replace('₹', '')
        discounted_price = discounted_price.replace(',', '')
        discounted_price = discounted_price.replace('Best Price*  ', '')
        discounted_price = discounted_price.replace('*', '')
        discounted_price = discounted_price.replace('Best', '')
        discounted_price = discounted_price.replace('Price', '')
        discounted_price = float(discounted_price)
    name = soup.find("h1", class_="black-txt")
    name = name.text.strip()
    element = soup.select_one('button[title="ADD TO CART"]')
    is_available = element is not None

    print(name)
    print(salt_name)
    print(price)
    print(discounted_price)
    print(is_available)
    medicine.salt_name = salt_name
    medicine.name = name
    medicine.is_available = is_available
    medicine.price = price or medicine.price
    medicine.discounted_price = discounted_price or medicine.discounted_price
    medicine.last_updated = datetime.datetime.now()
    medicine.save()
    return "DONE!"


# ONE-MG

@shared_task(bind=True)
def scrape_1mg(self, param):
    if param is None:
        return "DONE!"
    param = urllib.parse.quote(param)
    param = param.replace('/', '')
    print(param)
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
            is_available = False if ul_.find_element(By.CLASS_NAME, "style__not-available___ADBvR") else True
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
    if limit_threading:
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
    print("------------------------------  1 MG MEDICINE UPDATE ------------------------------------------")
    print(name)
    print(salt_name)
    print(original_price or discounted_price)
    print(discounted_price or original_price)
    print(is_available)
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
    param = urllib.parse.quote(param)
    param = param.replace('/', '')
    print(param)

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

        print(medicine_name)
        print(medicine_price)
        print(disc_price)
        print(image_url)

        medicine = Medicine.objects.filter(med_url=a_url).first()
        if medicine:
            medicine.is_available = is_available
            medicine.price = medicine_price or medicine.price
            medicine.discounted_price = disc_price or medicine.discounted_price
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
    if limit_threading:
        if medicine.last_updated and medicine.last_updated > timezone.now() - datetime.timedelta(days=1):
            return "Medicine already updated today!"
    response = requests.get(medicine.med_url)
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
    salt_name = seconds[generic_name].text.strip()

    print(name)
    print(price or disc_price)
    print(disc_price or price)
    print(salt_name)
    print(is_available)

    medicine.name = name or medicine.name
    medicine.price = price or disc_price if price is not None and disc_price is not None else medicine.price
    medicine.discounted_price = disc_price or price if price is not None and disc_price is not None else medicine.price
    medicine.salt_name = salt_name or medicine.salt_name
    medicine.is_available = is_available
    medicine.last_updated = datetime.datetime.now()
    medicine.save()
    return "DONE!"
