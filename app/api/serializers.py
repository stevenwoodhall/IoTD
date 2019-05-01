from manager.models import Device
from rest_framework import serializers
from dns.models import DNSQuery


class DNSQuerySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DNSQuery
        fields = ('id', 'datetime', 'domain', 'record', 'src')


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('last_seen', 'title', 'mac', 'ipv4', 'icon')


class DNSQueryTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DNSQuery
        fields = '__all__'
