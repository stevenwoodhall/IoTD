from .forms import SettingsForm
import subprocess
from .forms import DeviceForm
from django.shortcuts import get_object_or_404
from django.views import generic
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect
from .models import (Category, Device, Settings)
import json
import os
import django_tables2 as tables
from django.contrib.auth.decorators import login_required


@login_required
def apps(request):
    # find apps
    appList = []
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name == '_iot_module_.json':
                fp = os.path.join(root, name)
                appList.insert(0, fp)
    appList.sort()
    appData = {}
    for app in appList:
        with open(app, 'r+') as json_file:
            try:
                data = json.load(json_file)
                # Enable or Disable Apps
                if request.GET.get('toggle-app'):
                    appReq = request.GET.get('toggle-app')
                    if data['title'] == appReq:
                        with open(app, 'w') as json_file:
                            if data['enabled']:
                                data['enabled'] = False
                            else:
                                data['enabled'] = True
                            json_file.seek(0)
                            json.dump(data, json_file)
                            json_file.truncate()
                            return redirect('/api/restart-iotd/')
                appData[data['title']] = data
            except Exception as e:
                print(e)

    return render(
        request,
        'apps.html',
        context={'page_title': 'Apps', 'apps': appData}
    )


def index(request):
    """
    View function for home page of site.
    """
    return render(
        request,
        'landing.html'
    )


@login_required
def dashboard(request):

    devices_connected = Device.objects.all().count()

    try:
        from overwatch.models import Alert
        alerts = Alert.objects.all()
    except:
        alerts = {}

    try:
        from dns.functions import count_blocked_domains
    except:
        def count_blocked_domains():
            return None

    try:
        from api.functions import get_wifi_clients
        wifi_devices = get_wifi_clients()
    except:
        wifi_devices = {}

    return render(
        request,
        'dashboard.html',
        context={'page_title': 'Dashboard',
                 'devices_connected': devices_connected,
                 'wifi_devices': wifi_devices,
                 'domains_blocked': count_blocked_domains(),
                 'alerts': alerts}
    )


@login_required
def DeviceListView(request):
    devices = Device.objects.all().order_by('title')
    settings = Settings.objects.get(pk='settings')
    wifi_config = "WIFI:S:{};T:WPA;P:{};;".format(
        settings.wifi_ssid, settings.wifi_password)

    return render(request, 'devices/device_list.html',
                  {'page_title': 'Devices', 'object_list': devices,
                   'wifi_config': wifi_config, 'wifi_ssid': settings.wifi_ssid,
                   'wifi_password': settings.wifi_password})


@login_required
def device_detail_view(request, pk):
    dev = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DeviceForm(request.POST, instance=dev)
        # check whether it's valid:
        if form.is_valid():
            post = form.save()
            return redirect('/device/' + str(dev.id) + '?updated=true')
        else:
            return redirect('/device/' + str(dev.id) + '?updated=false')
    else:
        # fill in the current device data
        form = DeviceForm(instance=dev)

    try:
        from dns.models import (DNSQuery)

        class SimpleTable(tables.Table):
            class Meta:
                model = DNSQuery
                exclude = {'id', 'src'}
                template_name = 'django_tables2/bootstrap4.html'
        queryset = DNSQuery.objects.filter(src=dev.ipv4).values(
            'datetime', 'domain', 'record').order_by('-datetime')
        table = SimpleTable(queryset)
        table.paginate(page=request.GET.get('page', 1), per_page=15)

    except Exception as e:
        print(e)
        dns_queries = None

    return render(request, 'devices/device_detail.html',
                  context={'page_title': 'Device Info',
                           'device': dev, "dns_queries": table, 'form': form})


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@login_required
def lookup_device(request):
    try:
        mac = request.GET.get('mac')
        dev = get_object_or_404(Device, mac=mac)
        return redirect('/device/' + str(dev.id))
    except Exception as e:
        raise Http404(e)
        # raise Http404("Device does not exist")
    # return render_to_response('polls/detail.html')


# device api
@login_required
def delete_device(request):
    try:
        devid = request.GET.get('id')
        dev = get_object_or_404(Device, pk=devid)
        dev.delete()
        return redirect('/devices/')
    except Exception as e:
        raise Http404(e)


@login_required
def settings(request):
    set = get_object_or_404(Settings, pk='settings')
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=set)
        if form.is_valid():
            form.save()
            subprocess.call(["""sudo sed -i '/ssid/c\ssid={}'"""
                             """ /etc/hostapd/hostapd.conf""".format(
                                 form.cleaned_data['wifi_ssid'])], shell=True)
            subprocess.call(["""sudo sed -i '/wpa_passphrase/c"""
                             """\wpa_passphrase={}'"""
                             """/etc/hostapd/hostapd.conf""".format(
                                 form.cleaned_data['wifi_password'])],
                            shell=True)
            subprocess.run(['sudo', 'systemctl', 'restart',
                            'hostapd.service'], stdout=subprocess.PIPE)
            return redirect('/settings?updated=True')
    else:
        # fill in the current settings
        form = SettingsForm(instance=set)

    return render(request, 'settings.html', context={'page_title': 'Settings',
                                                     'form': form})
