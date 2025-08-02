from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DataAPIView(APIView):
    def get(self, request):
        data = []
        # from backend....
        return Response(data, status=status.HTTP_200_OK)
