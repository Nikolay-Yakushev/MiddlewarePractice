from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class Exception429View(APIView):
    def get(self, request, *args, **kwargs):
        """how to retrieve kwargs, args?"""
        return Response(data=kwargs.get("get", {"none": None}), status=status.HTTP_429_TOO_MANY_REQUESTS)
