from django.contrib.auth.models import User
from rest_framework import serializers

from backend_app.models import Poll, PollQuestion, PollQuestionChoices


class PollQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionChoices
        exclude = ("is_correct",)


class PollQuestionSerializer(serializers.ModelSerializer):
    choices = PollQuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = PollQuestion
        exclude = ("poll",)


class PollSerializer(serializers.ModelSerializer):
    questions = PollQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = "__all__"
