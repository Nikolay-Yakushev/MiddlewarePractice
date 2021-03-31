from rest_framework.generics import ListAPIView, RetrieveAPIView

# Create your views here.
from rest_framework.permissions import IsAuthenticated

from backend_app.models import Poll
from backend_app.serializers import PollSerializer


class TotalPollsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PollSerializer
    queryset = Poll.objects


class DetailPollView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PollSerializer
    lookup_field = "pk"
    queryset = Poll.objects
