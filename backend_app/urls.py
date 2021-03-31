from django.urls import path, include
from .views import TotalPollsView, DetailPollView


extra_urls = [
    path("", TotalPollsView.as_view(), name="TotalPollsView"),
    path("<int:pk>", DetailPollView.as_view(), name="DetailPollView"),
]
urlpatterns = [
    path("", include(extra_urls)),
]
