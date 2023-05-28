import json
import os
from uuid import uuid4

keyword = "dolo"  # required tag
"""
ISSUE WHEN SEARCHING IN 
Panadol
Disprine
Ecosprin 75
Pampers
dolo


"""

keylink = "https://healthplus.flipkart.com/willgo-sp-tablet-10-tab-aceclofenac-paracetamol-serratiopeptidase-mankind-pharma-ltd/medicine/hndse3"  # required link


def get_medicines(keyword):
    file_name = f"temp/{str(uuid4())}.json"
    cmd = f'python -m scrapy crawl health_plus -a input="{keyword}" -O "{file_name}" -L WARN'
    print(str(cmd))
    os.system(cmd)

    with open(file_name, "r", encoding="utf-8") as f:
        data_output = json.load(f)
    os.remove(file_name)
    data_output = data_output[:30]
    for x in data_output:
        print(x)
        product_image = x['ProductImage']
        product_image = f"https://res.fkhealthplus.com/incom/images/product/{x['ProductImage']}" if "http" not in product_image else product_image
        try:
            print(f'ProductName : ', x['ProductName'])
            print(f'Is Available : ', x['IsOutOfStock'] != 'Y')
            print(f'Salts : ', x.get('Salts').get('SaltStrengthRaw'))
            print(f'MRP : ', x['MRP'])
            print(f'Discounted Price : ', x['OfferPrice'])
            print(f'product_url : ', x['product_url'])
            print(f'ProductImage : ', product_image)
            print("==" * 20)
        except:
            pass
    # count = len(data_output)
    return data_output


def get_medicine_details(link):
    file_name = f"temp/{str(uuid4())}.json"
    cmd = f'python -m scrapy crawl health_plus_link -a input="{link}" -O "{file_name}"'
    print(str(cmd))
    os.system(cmd)
    with open(file_name, "r", encoding="utf-8") as f:
        data_output = json.load(f)
    os.remove(file_name)
    print(data_output)
    x = data_output[0]
    print(f'Name : ', x['name'])
    print(f'MRP : ', x['mrp_price'])
    print(f'Discounted_Price : ', x['price'])
    print(f'Is_available : ', 'InStock' in x['availability'])
    print("==" * 20)
    return data_output


if __name__ == '__main__':
    # keyword_details =
    get_medicines(keyword)
