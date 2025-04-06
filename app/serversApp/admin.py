from django.contrib import admin
from .models import Server,Article,ServerScreenshots,Carouser

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title','tags','image']
    

admin.site.register(Server)
admin.site.register(ServerScreenshots)
admin.site.register(Carouser)