from django.shortcuts import render,get_object_or_404,redirect
from .forms import NewUserForm, LoginForm
from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from .tasks import send_set_password_email_task
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse,HttpRequest
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
import base64
from serversApp.models import Server


def register(request):
    discord_url = settings.DISCORD_LOGIN_URL
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user_obj = CustomUser.objects.get(email=email)
            except:
                user_obj = None
            
            if user_obj:
                form = NewUserForm()
                return render(request,'registration/register.html',{'form':form,'discord_url':discord_url,'section':'register','error_message':'A user with this Email already exists.'})

            user = CustomUser(email=email)
            user.is_active = False
            user.save()

            site = get_current_site(request)
            
            mail_subject = 'Registration on the server monitoring site'
            message = render_to_string('email/set_password_email.html',{
                "user": user,
                'domain': site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_set_password_email_task.delay(mail_subject,message,email)

            return render(request,'registration/register_email_notification.html',{'email': email,'section':'register'})

    else:
        form = NewUserForm()

    
    return render(request,'registration/register.html',{'form':form,'discord_url':discord_url,'section':'register','error_message':''})

def login_view(request):
    discord_url = settings.DISCORD_LOGIN_URL
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            email = cd['username']
            password = cd['password']

            try:
                auth_user = authenticate(email=email, password=password)
                if auth_user.is_social:
                    return render(request,'registration/login.html',{'discord_url':discord_url,'error_message':'Your Email and password do not match. Please try again.','section':'login'})
                
                login(request, auth_user)
            except Exception as e:
                return render(request,'registration/login.html',{'discord_url':discord_url,'error_message':'Your Email and password do not match. Please try again.','section':'login'})

            return redirect('account')
        
    form = LoginForm()
    return render(request,'registration/login.html',{'discord_url':discord_url,'section':'login'})

def register_set_password(request,uidb64,token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_object_or_404(CustomUser,pk=uid)
    
    if default_token_generator.check_token(user,token):
        if request.method == 'POST':
            password = request.POST['password1']
            
            user.set_password(password)
            user.is_active = True
            user.is_social = False
            user.save()
            
            auth_user = authenticate(email=user.email, password=password)
            login(request, auth_user)

            return redirect('account')
        else:
            return render(request, 'registration/set_password.html',{'uid':uidb64,'token':token,'section':'register'})
    else:
        return HttpResponse('<h1>Invalid link</h1>')


def signup_redirect(request):
    
    return redirect('login')

def discord_login_redirect(request: HttpRequest):
    
    code = request.GET.get('code')
    user = exchange_code(code)

    find_user = CustomUser.objects.filter(email=user['email'])
    if len(find_user) == 0:
        new_user = CustomUser.objects.create(email=user['email'])
        new_user.set_password(user['id'])
        new_user.save()

        auth_user = authenticate(email = user['email'],password = user['id'])
        login(request,auth_user)

        return redirect('account')
    
    try:
        auth_user = authenticate(email = user['email'],password = user['id'])
        login(request,auth_user)

        return redirect('account')
    except:
        return redirect('login')
    


def exchange_code(code: str):
    data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f'{settings.SITE_URL}/user/discord_login/redirect/',
        'scope': 'email'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post('https://discord.com/api/oauth2/token',data=data,headers=headers)
    credentials = response.json()
    
    access_token = credentials['access_token']
    response = requests.get('https://discord.com/api/v6/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    user = response.json()
    return user

def discord_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            auth_user = authenticate(email=email, password=password)
            auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, auth_user)
            return redirect('account')
        except Exception as e:
            
            return render(request,'registration/discord_login.html',{'email': email,'section':'login','error_message':"Your Email and password do not match. Please try again."})


@login_required
def account_settings(request):
    if request.method == 'POST':
        new_email = request.POST['new_email']
        new_password = request.POST['new_password']

        if new_password and new_email == request.user.email:
            request.user.set_password(new_password)
            request.user.save()
            logout(request)
            return redirect('login')


        if new_email != request.user.email:
            try:
                CustomUser.objects.get(email=new_email)
                return render(request,'user/account_settings.html',{'error_message':'A user with this Email already exists.','section':'account','second_header_section': 'settings'})
            
            except CustomUser.DoesNotExist:
                pass

            uid = urlsafe_base64_encode(force_bytes(request.user.pk))
            token = default_token_generator.make_token(request.user)
            encoded_email = base64.b64encode(new_email.encode()).decode()

            site = get_current_site(request)
            
            mail_subject = 'Change email'
            message = render_to_string('email/change_email_mail.html',{
                "user": request.user,
                'domain': site.domain,
                'uid': uid,
                'token': token,
                'email': encoded_email
            })
            send_set_password_email_task.delay(mail_subject,message,request.user.email)
            
            return render(request,'registration/change_email_notification.html')
    
    return render(request,'user/account_settings.html', {'section':'account','second_header_section': 'settings'})

def change_email(request,uidb64,token,encoded_email):
    if default_token_generator.check_token(request.user,token):
        request.user.email = base64.b64decode(encoded_email.encode()).decode()
        
        request.user.save()
        return redirect('account')
    
    else:
        return HttpResponse('<h1>Invalid link</h1>')
    

@login_required
def my_servers(request):
    servers = Server.objects.filter(added=request.user)

    return render(request,'user/my_servers.html', {'servers': servers,'section':'account','second_header_section': 'my_servers'})
    