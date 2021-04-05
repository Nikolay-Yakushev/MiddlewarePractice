from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from backend_users.tests.users_info import get_users_info, get_headers_info
from unittest import mock
import fakeredis
# path("", UsersCreateView.as_view(), name="UsersCreateView"),
# path("log_in", LoginView.as_view(), name="LoginView"),
# path("log_out", LogoutView.as_view(), name="LogoutView"),
# path("all", ProtectedUrlPathView.as_view(), name="ProtectedUrlPathView"),
# path("unban", RemoveFromBannedView.as_view(), name="RemoveFromBannedView")


class UrlTestCases(TestCase):
    def get_url_path(self, name: str):
        return reverse(name)

    def setUp(self) -> None:
        users_info = get_users_info()
        counter = 1
        for user_info in users_info["users"]:
            user = User.objects.create(**user_info)
            user.set_password(f"test{counter}")
            counter += 1
            user.save()

        self.login_user1 = {"username": "TestUser1", "password": "test1"}

        self.login_user2 = {"username": "TestUser2", "password": "test2"}
        self.fake_login_user = {"username": "Hello", "password": "World"}

        User.objects.create_superuser("admin", "admin@myproject.com", "admin")
        self.login_user_admin = {"username": "admin", "password": "admin"}
        self.client = Client()

    def tearDown(self) -> None:
        pass

    def test_log_in(self):
        path = self.get_url_path("LoginView")
        response = self.client.get(path)
        self.assertEqual(response.status_code, 405)
        response = self.client.post(path, data=self.fake_login_user)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(path, data=self.login_user1)
        self.assertEqual(response.status_code, 200)

    #@@mock.patch("backend_users.middleware.IpCheckMiddleware")
    def test_request_limiter(self, mock_class):
        path = self.get_url_path("ProtectedUrlPathView")
        print(mock_class)
        # headers_choices = get_headers_info()
        # self.client.login(**self.login_user1)
        # for i in range(91):
        #     response = self.client.get(path, **random.choice(headers_choices))
        #
        #     self.assertEqual(response.status_code, 403)
        # for i in range(15):
        #     response = self.client.get(path, **random.choice(headers_choices))
        #     if i >= 9:
        #         self.assertEqual(response.status_code, 429)
        #     else:
        #         self.assertEqual(response.status_code, 403)
