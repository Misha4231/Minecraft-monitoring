from django.db import models
from django.contrib.postgres.fields import ArrayField
from userApp.models import CustomUser
from django.utils import timezone


class ServerScreenshots(models.Model):
    image = models.ImageField(upload_to='screenshots/%Y/%m/%d')

class Carouser(models.Model):
    image = models.ImageField(upload_to='carousel/%Y/%m/%d')

class Server(models.Model):
    title = models.CharField(max_length=1000, blank=True,null=True)
    short_description = models.CharField(max_length=150, blank=True,null=True)
    server_site = models.CharField(max_length=1000, blank=True,null=True)
    server_discord = models.CharField(max_length=1000, blank=True,null=True)
    full_description = models.CharField(max_length=3000,blank=True,null=True)
    version = models.CharField(max_length=100, blank=True,null=True)
    ip = models.CharField(max_length=1000,unique=True)
    is_icon_auto = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='logos/%Y/%m/%d',blank=True,null=True)
    server_banner = models.FileField(upload_to='beatiful/%Y/%m/%d',blank=True,null=True)
    screenshots = models.ManyToManyField(ServerScreenshots,related_name='server_screenshots', blank=True)
    carousel = models.ManyToManyField(Carouser,related_name='server_carousel', blank=True)
    curr_online = models.IntegerField(default=0,blank=True,null=True)
    max_online = models.IntegerField(default=0,blank=True,null=True)
    diamonds = models.IntegerField(default=0,blank=True,null=True)
    owners = models.ManyToManyField(CustomUser,related_name='servers',blank=True)
    added = models.ManyToManyField(CustomUser,related_name='added_servers',blank=True)
    status = models.BooleanField(default=True)
    who_polled = models.ManyToManyField(CustomUser,related_name='polled',blank=True)
    uptime = models.FloatField(default=0)

    last_check = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def row_index(self):
        ordered_servers = Server.objects.exclude(title__isnull=True).order_by('-diamonds')
        for index, server in enumerate(ordered_servers, start=1):
            if server == self:
                return index

    class Meta:
        verbose_name_plural = "Servers"

    def __str__(self) -> str:
        return self.ip
    
class Article(models.Model):
    title = models.CharField(max_length=1000)
    tags = ArrayField(models.CharField(max_length=100), blank=True,null=True)
    image = models.ImageField(upload_to='article_images/%Y/%m/%d')
    text = models.TextField()

    class Meta:
        verbose_name_plural = "Articles"

    def __str__(self) -> str:
        return self.title
    
class Donates(models.Model):
    createdAt = models.DateTimeField()
