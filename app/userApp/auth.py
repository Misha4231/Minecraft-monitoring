from typing import Any, Optional
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest
from .models import CustomUser


class DiscordAuthenticationBackend(BaseBackend):
    def authenticate(self,request,user) -> CustomUser:
        find_user = CustomUser.objects.filter(email=user['email'])
        if len(find_user) == 0:
            
            new_user = CustomUser.objects.create_user(email=user['email'],password=user['id'])

            return new_user
        
        return find_user[0]
