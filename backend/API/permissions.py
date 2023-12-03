from rest_framework.permissions import BasePermission

from .models import User

import redis
from backend.settings import REDIS_HOST, REDIS_PORT


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES["session_id"]
            if ssid is None:
                ssid = request.headers.get("authorization")
            if ssid is None:
                return False
        except:
            return False
        
        if session_storage.get(ssid):
            user = User.objects.get(username=session_storage.get(ssid).decode('utf-8'))
            return user.is_moderator or user.is_superuser
        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES["session_id"]
            if ssid is None:
                ssid = request.headers.get("authorization")
            if ssid is None:
                return False
        except:
            return False
        
        if session_storage.get(ssid):
            user = User.objects.get(username=session_storage.get(ssid).decode('utf-8'))
            return user.is_superuser
        return False
    
    
class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES.get("session_id")
            if ssid is None:
                ssid = request.headers.get("authorization")
            if ssid is None:
                return False
        except Exception as e:
            return False

        if session_storage.get(ssid):
            user = User.objects.get(username=session_storage.get(ssid).decode('utf-8'))
            return user.is_active

        return False
    

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator