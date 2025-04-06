from django.shortcuts import render,get_object_or_404,redirect
from .models import Server, Article,Carouser,ServerScreenshots
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.db.models.functions import RowNumber
import requests
from django.db.models import F,Window
from django.utils import timezone
from .forms import ServerForm
from django.http import JsonResponse
import os
from PIL import Image
from moviepy.editor import VideoFileClip
from django.conf import settings
from .tasks import remove_vote, minus_diamonds
from userApp.models import CustomUser
from moviepy.video.io.VideoFileClip import VideoFileClip
from io import BytesIO
import tempfile

def homepage(request):
    
    servers = Server.objects.exclude(title__isnull=True).annotate(row_number=Window(expression=RowNumber(), order_by=F('diamonds').desc())).order_by('-diamonds')

    paginator = Paginator(servers, 50)
    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    records_for_page = page.object_list
    articles = Article.objects.all()[:4]
    

    return render(request, 'home.html', {'section': 'home', 'page': page, 'servers': records_for_page,'articles':articles})


def server_detail(request,server_id):
    server = get_object_or_404(Server, pk=server_id)
    
    if server.uptime <= 0:
        uptime = 0
    else:
        req = requests.get(f'https://mcapi.us/server/status?ip={server.ip}')
        data = req.json()
        
        if data['online']:
            curr_time = timezone.now()
            uptime = ((server.uptime  + ((curr_time - server.last_check).total_seconds())) * 100) / (curr_time - server.created_at).total_seconds()
        else:
            curr_time = timezone.now()
            uptime = (server.uptime * 100) /(curr_time - server.created_at - (curr_time - server.last_check)).total_seconds()

        uptime = round(uptime,2)

    return render(request,'server_detail.html', {'server': server,'uptime': uptime, 'section': 'home'})

def free_daily_vote(request,server_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'To vote, you must log in or register!'})

    server = Server.objects.get(pk=server_id)
    print(server.who_polled.all())
    if request.user in server.who_polled.all():
        return JsonResponse({'error': 'You have already voted for this server today!'})
    
    server.diamonds += 1
    server.who_polled.add(request.user)
    server.save()

    remove_vote.apply_async(args=(server.pk, request.user.id), countdown=86400)
    minus_diamonds.apply_async(args=(server.pk, 1), countdown=2592000)

    return JsonResponse({'status': 'ok'})

def search_server(request):
    if request.method == 'POST':
        ip = request.POST['ip']

        try:
            server = Server.objects.get(ip=ip)
            return redirect('server_detail', server_id=server.pk)
        except:
            try:
                if ':' in ip:
                    r_ip = ip.split(':')[0]
                else:
                    r_ip = ip + ':25565'

                server = Server.objects.get(ip=r_ip)
                return redirect('server_detail', server_id=server.pk)
            except:
                return render(request, 'search_server.html', {'error_message': 'There is no such server for our site', 'section': 'search'})

    return render(request, 'search_server.html', {'section': 'search', 'error_message': ''})

def add_server(request):
    if request.method == 'POST' and request.user.is_authenticated:
        ip = request.POST['ip']
        req = requests.get(f'https://mcapi.us/server/status?ip={ip}')
        data = req.json()

        if not data['online']:
            return render(request,'create_server.html',{'section':'add','error_message': 'Such server does not exist.'})
        
        try:
            new_server = Server.objects.get(ip=ip)
        except Server.DoesNotExist:
            new_server = Server.objects.create(ip=ip)

        new_server.added.add(request.user)
        new_server.status = data['online']
        try:
            new_server.curr_online = data['players']['now']
            new_server.max_online = data['players']['max']
        except:
            pass
        new_server.save()

        return redirect('my_servers')
    
    else:
        return render(request,'create_server.html',{'section':'add'})
    


def validate_image_extension(file):
    valid_extensions = ['jpg', 'png','jpeg','jpe']
    ext = file.name.split('.')[1]
    if not ext.lower() in valid_extensions:
        return False
    return True

def validate_video_extension(file):
    valid_extensions = ['mp4', 'jpg', 'png', 'gif','jpeg','jpe']
    ext = file.name.split('.')[1]
    if not ext.lower() in valid_extensions:
        return False
    return True

def validate_image_resolution(width,height,image):
    with Image.open(image) as img:
        img_width, img_height = img.size
        if img_width == width and img_height == height:
            return True
        return False

def validate_video_resolution(width,height,video):
    video_bytes = video.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in video.chunks():
            temp_file.write(chunk)

    video_clip = VideoFileClip(temp_file.name)
    vid_width = video_clip.size[0]
    vid_height = video_clip.size[1]

    if height == vid_height and vid_width == width:
        return True
    return False


def edit_server_settings(request,id):
    server = Server.objects.get(pk=id)
    if request.user in server.owners.all() or request.user.is_superuser:
        icon_error = ''
        banner_error = ''
        carousel_error = ''
        scheenshots_error = ''
        if request.method == 'POST':
            form = ServerForm(request.POST, instance=server)
            if form.is_valid():
            
                if 'is_icon_auto' in request.POST:
                    server.is_icon_auto = True
                else:
                    server.is_icon_auto = False

                if 'server_banner' in request.FILES:
                    if validate_video_extension(request.FILES['server_banner']):
                        if request.FILES['server_banner'].name.endswith('.mp4'):
                            if validate_video_resolution(468,60,request.FILES['server_banner']):
                                server.server_banner = request.FILES['server_banner']
                            else:
                                banner_error = 'Wrong size'
                        else:
                            if validate_image_resolution(468,60,request.FILES['server_banner']):
                                server.server_banner = request.FILES['server_banner']
                            else:
                                banner_error = 'Wrong size'
                    else:
                        banner_error = 'Wrong size'

                if 'icon' in request.FILES:
                    if validate_image_extension(request.FILES['icon']):
                        if validate_image_resolution(64,64,request.FILES['icon']):
                            server.icon = request.FILES['icon']

                        else:
                            icon_error = 'Wrong size'

                    else:
                        icon_error = 'Wrong size'

                carousel = request.FILES.getlist('carousel')
                screenshots = request.FILES.getlist('screenshots')
                
                for carousel_image in carousel:
                    if validate_image_extension(carousel_image):
                        if validate_image_resolution(1920,600,carousel_image):
                            new_carousel = Carouser.objects.create(image=carousel_image)
                            server.carousel.add(new_carousel)
                        else:
                            carousel_error = 'Wrong size'
                    else:
                        carousel_error = 'Wrong size'
                
                for screenshor_image in screenshots:
                    if validate_image_extension(screenshor_image):
                        if validate_image_resolution(230,160,screenshor_image):
                            new_screenshots = ServerScreenshots.objects.create(image=screenshor_image)
                            server.screenshots.add(new_screenshots)
                        else:
                            scheenshots_error = 'Wrong size'
                    else:
                        scheenshots_error = 'Wrong size'

                form.save()
                server.save()

        return render(request,'edit_server_form.html',{'server':server,'icon_error': icon_error,'banner_error':banner_error,'carousel_error':carousel_error,'scheenshots_error':scheenshots_error})
    
    else:
        return redirect('homepage')
    
def delete_screenshot(request,server_id,screenshot_id):
    server = Server.objects.get(pk=server_id)
    if request.user in server.owners.all() or request.user.is_superuser:
        try:
            screenshot = ServerScreenshots.objects.get(pk=screenshot_id)
            server.screenshots.remove(screenshot)

            screenshot.delete()
        except:
            return JsonResponse({'status':'400'})

        return JsonResponse({'status':'ok'})

    return JsonResponse({'status':'400'})

def delete_carousel_image(request,server_id,carousel_image_id):
    server = Server.objects.get(pk=server_id)
    if request.user in server.owners.all() or request.user.is_superuser:
        try:
            image = Carouser.objects.get(pk=carousel_image_id)
            server.carousel.remove(image)

            image.delete()
        except:
            return JsonResponse({'status':'400'})

        return JsonResponse({'status':'ok'})

    return JsonResponse({'status':'400'})

def delete_banner_image(request,server_id):
    server = Server.objects.get(pk=server_id)
    if request.user in server.owners.all() or request.user.is_superuser:
        server.server_banner.delete(save=False)
        server.save()
        return JsonResponse({'status':'ok'})

    return JsonResponse({'status':'400'})

def diamond_price(request):
    dianonds = settings.CURRENCY_RELATION_DIAMOND
    uah = settings.CURRENCY_RELATION_USD

    return render(request,'diamond_price.html',{'diamonds':dianonds, 'uah':uah})

def donate_info(request):
    return render(request,'donate.html')


def articles_list(request):
    articles = Article.objects.all()
    return render(request,'article_list.html',{'articles': articles})

def article_detail(request,article_id):
    article = Article.objects.get(pk=article_id)
    return render(request,'article_detail.html', {'article': article})
