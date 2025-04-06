from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings

@shared_task()
def send_set_password_email_task(mail_subject,message,to_email):
    send_mail(subject = mail_subject, 
              message = message, 
              from_email = settings.EMAIL_HOST_USER, 
              recipient_list = [to_email], 
              fail_silently=False)
