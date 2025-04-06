# Generated by Django 4.2.3 on 2023-08-03 13:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('serversApp', '0009_server_created_at_server_last_check_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='server',
            name='last_check',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
