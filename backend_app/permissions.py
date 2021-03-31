# from django.contrib.auth import logout
# from rest_framework import permissions
# from rest_framework.exceptions import PermissionDenied
#
# from backend_users import redis_pi
#
#
# class CheckIpPermission(permissions.BasePermission):
#     message = "You're not allowed to perform this action"
#
#     def get_remote_addr(self, request):
#         return request.META['REMOTE_ADDR']
#
#
#
#     def has_permission(self, request, view):
#         get_ip = self.get_remote_addr(request)
#
#         else:
#             logout(request)
#             raise PermissionDenied()
