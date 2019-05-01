from django import forms
from django.forms import ModelForm
from .models import (Category, Device, Settings)


class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        fields = ['wifi_ssid', 'wifi_password',
                  'prowl_api_key', 'shodan_api_key']
        widgets = {
            'wifi_ssid': forms.TextInput(attrs={'class': 'form-control'}),
            'wifi_password': forms.TextInput(attrs={'class': 'form-control',
                                                    'minlength': 8}),
            'prowl_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'shodan_api_key': forms.TextInput(attrs={'class': 'form-control'})
        }


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = ['title', 'ipv4', 'mac', 'icon']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'ipv4': forms.TextInput(attrs={'class': 'form-control'}),
            'mac': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'})
        }
