from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('register_set_password/<str:uidb64>/<str:token>',views.register_set_password,name='register_set_password'),
    path('discord_login/redirect/',views.discord_login_redirect,name='discord_login_redirect'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

    path('account_settings/',views.account_settings,name='account'),
    path('my_servers/', views.my_servers, name='my_servers'),
    path('change_email/<str:uidb64>/<str:token>/<str:encoded_email>/',views.change_email,name='change_email'),
    path('discord_login/',views.discord_login,name='discord_login')
]