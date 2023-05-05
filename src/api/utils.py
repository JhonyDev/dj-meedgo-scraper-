NET_MEDS = 'Netmeds'
ONE_MG = '1Mg'
PHARM_EASY = 'PharmEasy'
FLIPCART = 'Flipkart Health'

LIST_PLATFORMS = [NET_MEDS, ONE_MG, PHARM_EASY, FLIPCART]

PLATFORMS = (
    ('1', NET_MEDS),
    ('2', ONE_MG),
    ('3', PHARM_EASY),
    ('4', FLIPCART),
)


def get_api_exception(detail, code):
    from rest_framework.exceptions import APIException
    api_exception = APIException()
    api_exception.status_code = code
    api_exception.detail = detail
    print(detail)
    return api_exception


def get_platform_dict():
    return {name: num for num, name in PLATFORMS}
