from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from . import redis_pi
from .middleware import IpCheckMiddleware
from .serializers import (
    RegisterSerializer,
    AuthenticationSerializer,
    UserSerializer,
    UnbanSubnetSerializer,
)


class UsersCreateView(CreateAPIView):
    queryset = User.objects
    serializer_class = RegisterSerializer

    def get(self, request, *args, **kwargs):
        data = {"create user"}
        return Response(data=data, status=status.HTTP_200_OK)


class LoginView(APIView):
    serializer_class = AuthenticationSerializer
    queryset = User.objects

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user:
            login(request, user)
            user_serializer = UserSerializer(user)
            user_data_json = JSONRenderer().render(user_serializer.data)
            redis_pi.set(name=user.id, value=user_data_json, ex=100)
            return Response(data=dict(Logged_in=True), status=status.HTTP_200_OK)

        return Response(
            data=dict(status_logged=False), status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return Response(data=dict(status_logged=False), status=status.HTTP_200_OK)


class ProtectedUrlPathView(ListAPIView):
    queryset = User.objects
    serializer_class = UserSerializer


class RemoveFromBannedView(APIView):
    serializer_class = UnbanSubnetSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        IpCheckMiddleware.remove_from_ban(serializer.validated_data["subnet_to_unban"])
        return Response(data=dict(status_unban=True), status=status.HTTP_200_OK)
