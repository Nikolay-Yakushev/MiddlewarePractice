import io
import os
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User, AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework.parsers import JSONParser

from Backend_Api.service_setup import subnet_vars_cfg
from backend_users import redis_pi

from django.http import HttpResponseForbidden, HttpResponse
from netaddr import IPNetwork, IPSet


def get_remote_addr(request):
    if "X-Forwarded-For" in request.headers:
        ip = request.headers["X-Forwarded-For"]
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip


def get_ipaddr(request):
    return IPNetwork(get_remote_addr(request))


def specify_prefixlen(ip: IPNetwork, prefix: int):
    ip.prefixlen = prefix
    return ip


def get_black_list_views(name: str):
    return getattr(settings, name, [])


def get_ipset_from_settings(name: str):
    return IPSet(getattr(settings, name, []))


class RedisAuthMiddleware(MiddlewareMixin):
    SESSION_KEY = "_auth_user_id"

    def __init__(self, get_response):
        super().__init__(get_response)

        self.get_response = get_response

    def get_user_or_anon(self, request):
        user = None
        session_key = request.COOKIES.get("sessionid", None)
        if session_key:
            """check if session is expired"""
            user_id = request.session[self.SESSION_KEY]
            user_data_json = redis_pi.get(name=user_id)
            if user_data_json is not None:
                stream = io.BytesIO(user_data_json)
                data = JSONParser().parse(stream)
                user = User(**data)

        return user or AnonymousUser()

    def __call__(self, request):
        # before view is called
        """add user to a request"""
        user = self.get_user_or_anon(request)
        request.user = SimpleLazyObject(lambda: user)
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response


class IpCheckMiddleware(MiddlewareMixin):
    banned_subnet = []

    def __init__(self, get_response):

        super().__init__(get_response)
        self.get_response = get_response
        self.ip_addrs = {}

    @classmethod
    def remove_from_ban(cls, subnet):
        cls.banned_subnet.remove(subnet)

    def check_ip(self, request):
        ip_raw = get_ipaddr(request)

        ip_pref_specified = specify_prefixlen(ip_raw, subnet_vars_cfg.SUBNET_PREFIX)
        """subnet_ntw - subnet of IP addr"""
        subnet_ntw = str(ip_pref_specified.network)
        print(subnet_ntw)
        if subnet_ntw in self.banned_subnet:
            ttl = redis_pi.ttl(subnet_ntw)
            if not ttl <= 0:
                """Check return time of unban"""
                return HttpResponse(
                    f"You will be unbanned in {ttl} seconds", status=429
                )
            """When ban time expires delete from banned"""
            IpCheckMiddleware.remove_from_ban(subnet_ntw)

        counter = redis_pi.get(name=subnet_ntw)

        if counter:
            if int(counter) == 100:
                self.banned_subnet.append(subnet_ntw)
                redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.WAIT_UNBAN_T)
                return HttpResponse(f"You are banned", status=429)
            redis_pi.incr(name=subnet_ntw, amount=1)
        else:
            """ 60 seconds to track ip_addr """

            redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.TRACK_IP_T)

    def __call__(self, request):
        # before view is called
        is_banned = self.check_ip(request)
        if is_banned:
            """return response for banned subnet"""
            return is_banned
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response


class WhiteListMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__()
        self.get_response = get_response

    def __call__(self, request):
        ip_addr = get_ipaddr(request)
        current_url = resolve(request.path_info)
        whitelist_ips = get_ipset_from_settings("ADMIN_WHITELIST")
        protected_urls = get_black_list_views("PROTECTED_URLS")

        if ip_addr not in whitelist_ips and current_url.url_name in protected_urls:
            raise PermissionDenied("You are not allowed to access this url")

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response
