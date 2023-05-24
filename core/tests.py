from __future__ import absolute_import, unicode_literals

import datetime

from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.api.models import Medicine
from src.api.utils import get_platform_dict, NET_MEDS

url = f"https://www.netmeds.com/catalogsearch/result/pana/all"
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
            # update_medicine.delay(check_med.id)
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
