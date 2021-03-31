from django.urls import path
from .views import (
    UsersCreateView,
    LoginView,
    LogoutView,
    ProtectedUrlPathView,
    RemoveFromBannedView,
)

urlpatterns = [
    path("", UsersCreateView.as_view(), name="UsersCreateView"),
    path("log_in", LoginView.as_view(), name="LoginView"),
    path("log_out", LogoutView.as_view(), name="LogoutView"),
    path("all", ProtectedUrlPathView.as_view(), name="ProtectedUrlPathView"),
    path("unban", RemoveFromBannedView.as_view(), name="RemoveFromBannedView")
    # path("auth/", BackendAccessView.as_view(), name='BackendAccessView'),
]
