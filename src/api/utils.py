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


def balance_medicines(instance):
    from django.db import transaction
    from src.api.models import MedicineOfferBridge
    medicines = MedicineOfferBridge.objects.filter(order_grab=instance).values('medicine__pk')
    remaining_medicines = instance.order_request.medicine_cart.medicines.exclude(pk__in=medicines)
    with transaction.atomic():
        for medicine in remaining_medicines:
            MedicineOfferBridge.objects.create(order_grab=instance, medicine=medicine)


def get_similarity_queryset(queryset, param1, salt_name=None, is_salt=False):
    print("||" * 100)
    from fuzzywuzzy import fuzz
    # if is_salt:
    #     similar_words = queryset.exclude(salt_name=None).values('pk', 'name', 'salt_name')
    # else:
    #     similar_words = queryset.values('pk', 'name', 'salt_name')

    similar_words = queryset.values('pk', 'name', 'salt_name')
    similar_words_ = []
    similarities = []
    similarities_map = {}
    for word in similar_words:
        ratio_name = fuzz.ratio(param1, word['name'])
        if is_salt:
            ratio_salt = fuzz.ratio(salt_name, word['salt_name'])
            net_ratio = (ratio_salt + ratio_name) / 2
            print(f'{param1} - {salt_name} COMPARING TO')
            print(f'{word["name"]} - {word["salt_name"]} = {net_ratio}')
        else:
            ratio_salt = fuzz.ratio(param1, word['salt_name'])
            net_ratio = (ratio_salt + ratio_name) / 2

        check = 50 if not is_salt else 30
        if net_ratio > check:
            similar_words_.append(word['pk'])
            similarities.append(net_ratio)
            similarities_map[net_ratio] = word['pk']
    similarities.sort()
    similarities.reverse()
    # sorted_similar_words = [similarities_map[x] for x in similarities]
    queryset = queryset.filter(pk__in=similar_words_)
    # order_dict = {word: index for index, word in enumerate(sorted_similar_words)}
    # queryset = queryset.annotate(custom_order=models.Case(
    #     *[models.When(pk=pk, then=models.Value(order)) for pk, order in order_dict.items()],
    #     default=models.Value(len(order_dict))
    # ))
    #
    # return queryset.order_by('custom_order')
    return queryset
