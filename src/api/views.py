from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class APIHomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response(data={"detail": f'Test Api'},
                        status=status.HTTP_202_ACCEPTED)
