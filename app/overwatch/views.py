from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import django_tables2 as tables
from datetime import datetime
from .models import (Alert, Host)
from manager.models import Settings

import requests
import shodan
import json


@login_required
def overwatch_summary(request):
    class SimpleTable(tables.Table):
        class Meta:
            model = Alert
            exclude = {'id'}
            template_name = 'django_tables2/bootstrap4.html'

    settings = Settings.objects.get(pk='settings')
    try:
        publicIPv4 = requests.get('https://api.ipify.org').text
    except:
        publicIPv4 = None

    host = {}
    if settings.shodan_api_key:
        shodanAPI = shodan.Shodan(settings.shodan_api_key)
        if publicIPv4:
            try:
                host = shodanAPI.host(publicIPv4)
                # change date to python datetime object
                host['last_update'] = datetime.strptime(
                    host['last_update'], '%Y-%m-%dT%H:%M:%S.%f')
                # update database
                hostObj, created = Host.objects.get_or_create(
                    last_update=host['last_update'], ip_str=host['ip_str'],
                    ports=json.dumps(host['ports']))

            except shodan.APIError as e:
                if str(e).strip() == "No information available for that IP.":
                    host["error"] = "Shodan does not currently have any" \
                        " information for your IP ({}).".format(
                        publicIPv4)
                elif str(e).strip() == "API access denied":
                    host["error"] = "You Shodan API doesn't"
                    " seem to be working."
                else:
                    host["error"] = "Shodan API Error: {}".format(e)
        else:
            host["error"] = "Failed to identify your IP address"
    else:
        host["error"] = "No Shodan API Key"

    # Tables
    # Create Shodan History table
    shodan_history = Host.objects.all().order_by('-last_update')[:10]
    # Alerts
    queryset = Alert.objects.all().order_by('-datetime')

    class SimpleTable(tables.Table):
        class Meta:
            model = Alert
            exclude = {'id', 'mac', 'dismissed'}
            template_name = 'django_tables2/bootstrap4.html'
    table = SimpleTable(queryset)
    table.paginate(page=request.GET.get('page', 1), per_page=15)

    return render(
        request,
        'overwatch_summary.html',
        context={'page_title': 'Overwatch',
                 'alerts': table, 'settings': settings, 'shodan': host,
                 'shodan_history': shodan_history}
    )
