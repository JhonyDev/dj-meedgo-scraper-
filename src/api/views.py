from django.db.models import F, Q
from django.shortcuts import redirect
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.settings import PHARM_EASY, NET_MEDS, ONE_MG
from src.api import tasks
from src.api.models import Medicine
from src.api.tasks import update_medicine_pharmeasy, update_medicine, update_medicine_1mg
from src.api.utils import get_platform_dict


class ScrapeMedicineAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        param = self.request.query_params.get('search')
        if param:
            tasks.scrape_flipkart.delay(param)
            tasks.scrape_pharmeasy.delay(param)
            tasks.scrape_netmeds.delay(param)
            tasks.scrape_1mg.delay(param)
            return Response({"message": "Added param to scraper queue"}, status.HTTP_200_OK)
        return Response({"message": "Search String not found"}, status.HTTP_400_BAD_REQUEST)


class ScrapeNetmedsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        param = self.request.query_params.get('search')
        if param:
            tasks.scrape_netmeds.delay(param)
            return Response({"message": "Added param to scraper queue"}, status.HTTP_200_OK)
        return Response({"message": "Search String not found"}, status.HTTP_400_BAD_REQUEST)


class ScrapePharmeasyAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        param = self.request.query_params.get('search')
        if param:
            tasks.scrape_pharmeasy.delay(param)
            return Response({"message": "Added param to scraper queue"}, status.HTTP_200_OK)
        return Response({"message": "Search String not found"}, status.HTTP_400_BAD_REQUEST)


class ScrapeOneMgAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        param = self.request.query_params.get('search')
        if param:
            tasks.scrape_1mg.delay(param)
            return Response({"message": "Added param to scraper queue"}, status.HTTP_200_OK)
        return Response({"message": "Search String not found"}, status.HTTP_400_BAD_REQUEST)


class ScrapeFlipkartAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        param = self.request.query_params.get('search')
        if param:
            tasks.scrape_flipkart.delay(param)
            return Response({"message": "Added param to scraper queue"}, status.HTTP_200_OK)
        return Response({"message": "Search String not found"}, status.HTTP_400_BAD_REQUEST)


def custom_method_view(request, object_id):
    # import csv
    # with open('med_names.csv', 'r') as file:
    #     csv_reader = csv.reader(file)
    #     for row in csv_reader:
    #         for value in row:
    #             # scrape_1mg.delay(value)
    #             # scrape_flipkart.delay(value)
    #             # scrape_netmeds.delay(value)
    #             scrape_pharmeasy.delay(value)

    med = Medicine.objects.get(pk=object_id)
    if med.platform == get_platform_dict()[PHARM_EASY]:
        update_medicine_pharmeasy(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[NET_MEDS]:
        all_meds = Medicine.objects.filter(platform=get_platform_dict()[NET_MEDS], salt_name=None,
                                           price=None, discounted_price=None).values_list('pk', flat=True)
        for med_ in all_meds:
            update_medicine.delay(med_, is_forced=True)
        update_medicine(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[ONE_MG]:
        update_medicine_1mg(med.pk, is_forced=True)
    return redirect('admin:api_medicine_change', object_id)


def custom_method_all_view(request, object_id):
    med = Medicine.objects.get(pk=object_id)
    queryset = Medicine.objects.filter(
        Q(name='') |
        Q(salt_name__isnull=True) |
        Q(price__isnull=True) |
        Q(discounted_price__isnull=True) |
        Q(price=F('discounted_price'))
    )
    if med.platform == get_platform_dict()[PHARM_EASY]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[PHARM_EASY]).values_list('pk', flat=True):
            update_medicine_pharmeasy.delay(med_, is_forced=True)
        update_medicine_pharmeasy(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[NET_MEDS]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[NET_MEDS]).values_list('pk', flat=True):
            update_medicine.delay(med_, is_forced=True)
        update_medicine(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[ONE_MG]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[ONE_MG]).values_list('pk', flat=True):
            update_medicine_1mg.delay(med_, is_forced=True)
        update_medicine_1mg(med.pk, is_forced=True)
    return redirect('admin:api_medicine_change', object_id)
