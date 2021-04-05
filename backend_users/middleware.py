import io
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User, AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.http import JsonResponse
from Backend_Api.service_setup import subnet_vars_cfg
from backend_users import redis_pi
from netaddr import IPNetwork, IPSet
from django.utils.http import urlencode


def get_remote_addr(request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip


def build_url(*args, **kwargs):

    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url = f"{url}?{urlencode(get)}"
    return url


def get_429_response(data: dict):
    response = Response(data=data,

                        status=status.HTTP_429_TOO_MANY_REQUESTS, content_type="application/json"
                        )
    return response


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

    def get_ip_subnet(self, request):
        ip_raw = get_ipaddr(request)
        ip_pref_specified = specify_prefixlen(ip_raw, subnet_vars_cfg.SUBNET_PREFIX)
        return ip_pref_specified

    def check_ip_subnet(self, subnet_ntw: str):
        """subnet_ntw - subnet of IP addr"""
        if subnet_ntw in self.banned_subnet:
            return True
        return False

    def get_ttl_to_unban(self, subnet_ntw):
        ttl = redis_pi.ttl(subnet_ntw)
        return ttl

    def remove_from_banned(self, subnet_ntw):
        """When ban time expires delete from banned"""
        IpCheckMiddleware.remove_from_ban(subnet_ntw)
        """TRACK_IP_T - during this period of time ip is tracked"""
        redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.TRACK_IP_T)

    def first_layer_check(self, subnet_ntw):
        ttl_left = 0
        status_ban = False
        is_banned = self.check_ip_subnet(subnet_ntw)
        if is_banned:
            ttl = self.get_ttl_to_unban(subnet_ntw)
            if ttl > 0:
                status_ban = True
                ttl_left = ttl
            else:
                self.remove_from_banned(subnet_ntw)
                redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.TRACK_IP_T)
                status_ban = False
        return status_ban, ttl_left

    def second_layer_check(self, subnet_ntw):
        status_ban, ttl_left = False, 0
        counter = redis_pi.get(name=subnet_ntw)
        if counter:
            if int(counter) >= subnet_vars_cfg.TOTAL_REQUEST:
                self.banned_subnet.append(subnet_ntw)
                redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.WAIT_UNBAN_T)
                status_ban = True
                ttl_left = subnet_vars_cfg.WAIT_UNBAN_T
            else:
                redis_pi.incr(name=subnet_ntw, amount=1)
        else:
            """TRACK_IP_T seconds to track ip_addr """
            redis_pi.set(name=subnet_ntw, value=1, ex=subnet_vars_cfg.TRACK_IP_T)

        return status_ban, ttl_left

    def __call__(self, request):
        # before view is called
        ip_subnet = self.get_ip_subnet(request)
        subnet_ntw = str(ip_subnet.network)
        is_banned, ttl = self.first_layer_check(subnet_ntw)
        if is_banned is True:
            data = {
                'status_ban': True,
                'time_left': ttl}
            return JsonResponse(data, status=429)
        is_banned, ttl = self.second_layer_check(subnet_ntw)
        if is_banned is True:
            data = {
                'status_ban': True,
                'time_left': ttl}

            return JsonResponse(data, status=429)

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
