from django.urls import path, include

from .exceptions_view import Exception429View
from .views import (
    UsersCreateView,
    LoginView,
    LogoutView,
    ProtectedUrlPathView,
    RemoveFromBannedView,
)

extra_patterns = [
    path(
        "429",
        Exception429View.as_view(),
        name="Exception429View"
    ),
]

urlpatterns = [
    path("", UsersCreateView.as_view(), name="UsersCreateView"),
    path("log_in", LoginView.as_view(), name="LoginView"),
    path("log_out", LogoutView.as_view(), name="LogoutView"),
    path("all", ProtectedUrlPathView.as_view(), name="ProtectedUrlPathView"),
    path("unban", RemoveFromBannedView.as_view(), name="RemoveFromBannedView"),
    path("exceptions/", include(extra_patterns))
    # path("auth/", BackendAccessView.as_view(), name='BackendAccessView'),
]
