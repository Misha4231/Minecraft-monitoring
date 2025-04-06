from django.urls import path
from . import views

urlpatterns = [
    path('server_detail/<int:server_id>/', views.server_detail,name='server_detail'),
    path('search_server/',views.search_server,name='search_server'),
    path('add_server/', views.add_server, name='add_server'),
    path('edit_server_settings/<int:id>/', views.edit_server_settings, name='edit_server_settings'),
    path('delete_screenshot/<int:server_id>/<int:screenshot_id>/', views.delete_screenshot,name='delete_screenshot'),
    path('delete_carousel_image/<int:server_id>/<int:carousel_image_id>/', views.delete_carousel_image,name='delete_carousel_image'),
    path('diamond_price/', views.diamond_price,name='diamond_price'),
    path('donate_info/', views.donate_info,name='donate_info'),
    path('articles_list/',views.articles_list,name='articles_list'),
    path('article_detail/<int:article_id>/',views.article_detail,name='article_detail'),
    path('free_daily_vote/<int:server_id>/', views.free_daily_vote, name='free_daily_vote'),
    path('delete_banner_image/<int:server_id>/', views.delete_banner_image,name='delete_banner_image'),
]