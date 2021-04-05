from django.contrib.auth.models import User


def get_users_info():
    users_list = {
        "users": [
            dict(
                username="TestUser1",
                first_name="TestUserFirstName1",
                last_name="TestUserLastName1",
                email="TestUser1@email.com",
            ),
            dict(
                username="TestUser2",
                first_name="TestUserFirstName2",
                last_name="TestUserLastName2",
                email="TestUser2@email.com",
            ),
        ]
    }
    return users_list


def get_headers_info():
    headers1 = {"X-Forwarded-For": "127.67.34.12"}
    headers2 = {"X-Forwarded-For": "127.67.34.67"}
    return [headers1, headers2]
