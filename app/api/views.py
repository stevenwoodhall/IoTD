from .functions import get_wifi_clients
from rest_framework import generics
from rest_framework.settings import api_settings
from .functions import get_dns_data
from datetime import datetime
import re
import datetime
import itertools
from rest_framework.views import APIView
import subprocess
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions

from dns.models import DNSQuery
from .serializers import DeviceSerializer, DNSQuerySerializer
from .serializers import DNSQueryTableSerializer

from manager.models import Device


class DNSQueryViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = DNSQuery.objects.all()
    serializer_class = DNSQuerySerializer


class DeviceViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


@api_view(['GET'])
def WiFiDevicesViewSet(request):
    """
    Dump wifi station and return JSON.
    """
    if request.method == 'GET':
        return Response(get_wifi_clients())
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API for shutdown and restart options


@login_required
def restart_device(request):
    cmd = subprocess.run(['sudo', 'reboot'], stdout=subprocess.PIPE)
    return redirect('/')


@login_required
def shutdown_device(request):
    cmd = subprocess.run(['sudo', 'shutdown', 'now'], stdout=subprocess.PIPE)
    return redirect('/')


@login_required
def restart_iotd(request):
    cmd = subprocess.run(['sudo', 'systemctl', 'restart',
                          'iotd-django.service'], stdout=subprocess.PIPE)
    return redirect('/')


# Charts
class DNSQueryChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        last_x_days = datetime.datetime.today() - datetime.timedelta(30)
        objs = DNSQuery.objects.filter(
            datetime__gte=last_x_days).values("datetime")
        grouped = itertools.groupby(
            objs, lambda record: record.get("datetime").strftime("%Y-%m-%d"))
        objs_by_day = [(day, len(list(objs_this_day)))
                       for day, objs_this_day in grouped]

        labels_l = []
        data_d = []
        for x in objs_by_day:
            l, d = x
            if l not in labels_l:
                labels_l.append(l)
                data_d.append(d)

        data = {'labels': labels_l, 'data': data_d}

        return Response(data)


class DNSQueryTableData(ModelViewSet):

    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        page = request.query_params.get('page')
        perPage = request.query_params.get('perPage')
        offset = request.query_params.get('offset')
        search = request.query_params.get('queries[search]')
        # calculate pagination
        total = (int(perPage) * int(page))

        # search for specific domains
        if search:
            queryset = DNSQuery.objects.all().filter(
                domain__contains=search).order_by('-datetime')
        else:
            queryset = DNSQuery.objects.all().order_by('-datetime')
        dnsResults = DNSQuerySerializer(queryset, many=True).data
        custom_data = {
            'records': dnsResults[int(offset):total]
        }
        if len(dnsResults):
            query = total
        else:
            query = 0
        custom_data.update({
            'totalRecordCount': len(dnsResults),
            'queryRecordCount': query
        })
        return Response(custom_data)
