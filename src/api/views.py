from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ScrapeMedicineAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # TODO: Check asdasd asdasd

        return Response({"": ""}, status.HTTP_200_OK)
