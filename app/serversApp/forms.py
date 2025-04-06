from django import forms
from .models import Server


class ServerForm(forms.ModelForm):
    class Meta:
        fields = ['title','short_description','server_site','server_discord','full_description','version','ip','is_icon_auto']
        model = Server