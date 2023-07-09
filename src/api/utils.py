from src.api.models import MedicineCartBridge, UserRating


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
    print("/" * 100)
    # from fuzzywuzzy import fuzz
    #
    # similar_words = queryset.order_by(
    #     'name', 'salt_name').distinct('name', 'salt_name').values('pk', 'name', 'salt_name')
    # print(len(similar_words))
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
    #     if len(similarities) > 10:
    #         break
    # similarities.sort()
    # similarities.reverse()
    # queryset = queryset.filter(pk__in=similar_words_)
    #
    # sorted_similar_words = [similarities_map[x] for x in similarities]
    # order_dict = {word: index for index, word in enumerate(sorted_similar_words)}
    # queryset = queryset.annotate(custom_order=Case(
    #     *[When(pk=pk, then=Value(order)) for pk, order in order_dict.items()],
    #     default=Value(len(order_dict))
    # ))

    from elasticsearch_dsl import Search
    from elasticsearch_dsl.query import MultiMatch
    print(salt_name)
    search = Search(index='medicine')
    search = search.query(
        MultiMatch(
            query=salt_name,
            fields=['name', 'salt_name'],
            fuzziness='AUTO',
            prefix_length=2,
            max_expansions=100,
            tie_breaker=0.0
        )
    )
    results = search.execute()
    results = [x.id for x in results.hits[:5]]
    queryset = queryset.filter(pk__in=results)
    print(queryset)
    return queryset


def get_average_rating(user):
    from django.db.models import Avg
    average_rating = UserRating.objects.filter(given_to=user).aggregate(avg_rating=Avg('rating'))
    avg_rating_value = average_rating['avg_rating']
    return avg_rating_value
