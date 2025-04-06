from monitoring.celery import app
from celery import shared_task
from .models import Server,Donates
import requests
from django.utils import timezone
from django.conf import settings
import datetime
import time
from django.utils.timezone import make_aware
from userApp.models import CustomUser

@shared_task
def get_new_server_info():
    servers = Server.objects.all()

    for server in servers:
        req = requests.get(f'https://mcapi.us/server/status?ip={server.ip}')
        data = req.json()

        try:
            server.status = data['online']
            server.curr_online = data['players']['now']
            server.max_online = data['players']['max']

            if data['online']:
                current_time = timezone.now()

                time_difference = (current_time - server.last_check).total_seconds()
                server.uptime += time_difference

            server.last_check = timezone.now()

            server.save()
        except Exception as e:
            print(e)

@shared_task
def minus_diamonds(server_id,diamonds):

    server = Server.objects.get(pk=server_id)
    server.diamonds -= diamonds
    server.save()


@shared_task
def get_new_donates():
    all_donates_req = requests.get('https://donatello.to/api/v1/donates',headers={'X-Token': settings.DONATELLO_API_TOKEN})
    all_donates = all_donates_req.json()

    try:
        last_donate = Donates.objects.last()
        last_time_donate = last_donate.createdAt
    except:
        last_time_donate = datetime.datetime(1900,1,1,1,1,1,1)
    
    try:
        for donate in all_donates['content']:
            donate_datetime = datetime.datetime.strptime(donate['createdAt'],"%Y-%m-%d %H:%M:%S")

            donate_datetime = donate_datetime.astimezone(timezone.utc)
            last_time_donate = last_time_donate.astimezone(timezone.utc)

            if last_time_donate < donate_datetime:
                try:
                    server = Server.objects.get(ip=donate['message'])
                except:
                    server = None

                if server:
                    new_diamonds = (float(donate['amount']) / settings.CURRENCY_RELATION_USD) * settings.CURRENCY_RELATION_DIAMOND
                    server.diamonds += new_diamonds

                    minus_diamonds.apply_async(args=(server.id, new_diamonds), countdown=2592000)

                    server.save()

                    new_donate_record = Donates.objects.create(createdAt = donate_datetime)
                    new_donate_record.save()
    except:
        pass


@shared_task
def remove_vote(server_id,user_id):
    server = Server.objects.get(pk=server_id)
    user = CustomUser.objects.get(pk=user_id)

    server.who_polled.remove(user)
    server.save()

    