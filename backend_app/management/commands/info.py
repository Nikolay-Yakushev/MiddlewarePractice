def get_polls():
    polls_list = [
        dict(
            poll_title="Природные ископаемые",
            poll_description="опрос про природные ископаемые",
            questions=[
                dict(
                    question_name="Как называют брилианты до обрабоки?",
                    choices=[
                        dict(choice_name="Изумруд", is_correct=False),
                        dict(choice_name="Неограненный бриллиант", is_correct=False),
                        dict(choice_name="Рубин", is_correct=False),
                        dict(choice_name="Алмаз", is_correct=True),
                    ],
                ),
                dict(
                    question_name="В честь чего назван минерал Танзанит?",
                    choices=[
                        dict(
                            choice_name="В чеесть императора Танзании - Танзанития 4-го",
                            is_correct=False,
                        ),
                        dict(
                            choice_name="В честь начедшего минерал исследователя  - Мркуса Тансона",
                            is_correct=False,
                        ),
                        dict(choice_name="В честь старны - Таназнии ", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Какой драгоценный металл не подвержен коррозии?",
                    choices=[
                        dict(choice_name="Медь", is_correct=False),
                        dict(choice_name="Золото", is_correct=True),
                    ],
                ),
            ],
        ),
        dict(
            poll_title="Космос",
            poll_description="опрос про космос",
            questions=[
                dict(
                    question_name="Как называют галактику в который мы находимся?",
                    choices=[
                        dict(choice_name="Андромеда", is_correct=False),
                        dict(choice_name="Пегас", is_correct=False),
                        dict(choice_name="Млечный Путь", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Самая большая планета в солнечной системе?",
                    choices=[
                        dict(choice_name="Солнце", is_correct=False),
                        dict(
                            choice_name="Нептун",
                            is_correct=False,
                        ),
                        dict(choice_name="Юпитер", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Сколько спутников у Сатурна?",
                    choices=[
                        dict(choice_name="33", is_correct=False),
                        dict(choice_name="83", is_correct=True),
                    ],
                ),
            ],
        ),
    ]
    return polls_list
