"""
URL configuration for monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from userApp.views import signup_redirect
from django.conf import settings
from django.conf.urls.static import static
from serversApp.views import homepage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('userApp.urls')),
    path('accounts/social/signup/',signup_redirect,name='signup_redirect'),
    path('accounts/', include('allauth.urls')),
    path('servers/',include('serversApp.urls')),

    path('',homepage,name='homepage'),
]
#127.0.0.1:8000/accounts/social/signup/


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)