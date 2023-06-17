from src.api.models import MedicineCartBridge, Medicine


def get_api_exception(detail, code):
    from rest_framework.exceptions import APIException
    api_exception = APIException()
    api_exception.status_code = code
    api_exception.detail = detail
    print(detail)
    return api_exception


def get_platform_dict():
    from core.settings import PLATFORMS
    return {name: num for num, name in PLATFORMS}


def balance_medicines(instance):
    from django.db import transaction
    from src.api.models import MedicineOfferBridge
    medicines = MedicineOfferBridge.objects.filter(order_grab=instance).values('medicine_cart_bridge__pk')
    medicine_cart_bridges = MedicineCartBridge.objects.filter(
        medicine_card=instance.order_request.medicine_cart).exclude(pk__in=medicines)
    with transaction.atomic():
        for medicine_cart_bridge in medicine_cart_bridges:
            MedicineOfferBridge.objects.create(medicine_cart_bridge=medicine_cart_bridge, order_grab=instance)


def get_similarity_queryset(queryset, param1, salt_name=None, is_salt=False):
    print("||" * 100)
    #
    # from fuzzywuzzy import fuzz
    # # if is_salt:
    # #     similar_words = queryset.exclude(salt_name=None).values('pk', 'name', 'salt_name')
    # # else:
    # #     similar_words = queryset.values('pk', 'name', 'salt_name')
    #
    # similar_words = queryset.values('pk', 'name', 'salt_name')
    # similar_words_ = []
    # similarities = []
    # similarities_map = {}
    # for word in similar_words:
    #     ratio_name = fuzz.ratio(param1, word['name'])
    #     if is_salt:
    #         ratio_salt = fuzz.ratio(salt_name, word['salt_name'])
    #         net_ratio = (ratio_salt + ratio_name) / 2
    #     else:
    #         ratio_salt = fuzz.ratio(param1, word['salt_name'])
    #         net_ratio = (ratio_salt + ratio_name) / 2
    #     check = 50 if not is_salt else 30
    #     if net_ratio > check:
    #         similar_words_.append(word['pk'])
    #         similarities.append(net_ratio)
    #         similarities_map[net_ratio] = word['pk']
    # similarities.sort()
    # similarities.reverse()
    # queryset = queryset.filter(pk__in=similar_words_)

    # sorted_similar_words = [similarities_map[x] for x in similarities]
    # order_dict = {word: index for index, word in enumerate(sorted_similar_words)}
    # queryset = queryset.annotate(custom_order=models.Case(
    #     *[models.When(pk=pk, then=models.Value(order)) for pk, order in order_dict.items()],
    #     default=models.Value(len(order_dict))
    # ))
    #
    # return queryset.order_by('custom_order')
    from django.contrib.postgres.search import SearchVector
    from django.contrib.postgres.search import SearchQuery
    from django.contrib.postgres.search import SearchRank
    search_vector = (
        SearchVector('name', weight='A')
    )

    search_query = (
        SearchQuery(param1)
    )

    ranked_medicines = (
        Medicine.objects.annotate(
            rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.1).order_by('-rank')[:10]
        # .values('medicine_name', 'rank')
    )
    return ranked_medicines
