from django.core.management import BaseCommand
from .info import get_polls
from backend_app.models import Poll, PollQuestion, PollQuestionChoices


class Command(BaseCommand):
    help = "Create Polls objects"

    def handle(self, info_tests=None, *args, **options):
        self.polls_data = get_polls()
        for data_p in self.polls_data:
            poll_q = data_p.pop("questions")
            poll = Poll.objects.create(**data_p)
            for question in poll_q:
                choices = question.pop("choices")
                question = PollQuestion.objects.create(**question, poll=poll)
                PollQuestionChoices.objects.bulk_create(
                    [
                        PollQuestionChoices(question=question, **choice_data)
                        for choice_data in choices
                    ]
                )
