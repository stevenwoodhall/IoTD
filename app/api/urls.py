from .views import DNSQueryChartData, DNSQueryTableData
from .views import shutdown_device
from .views import restart_iotd
from .views import restart_device
from .views import WiFiDevicesViewSet
from .views import DeviceViewSet
from .views import DNSQueryViewSet
from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token, name='api_token_auth')
]


urlpatterns += [
    url(
        r'^dns-query/$',
        DNSQueryViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='dns-query-list',
    ),
    url(
        r'^dns-query/(?P<pk>\d+)/$',
        DNSQueryViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update',
             'delete': 'destroy'}),
        name='dns-query-detail',
    )
]

# add device api

urlpatterns += [
    url(
        r'^devices/$',
        DeviceViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='devices-list',
    ),
    url(
        r'^devices/(?P<pk>\d+)/$',
        DeviceViewSet.as_view({'get': 'retrieve', 'put': 'update',
                               'patch': 'partial_update',
                               'delete': 'destroy'}),
        name='devices-detail',
    )
]

# add custom api

urlpatterns += [
    url(
        r'^wifi-devices/$',
        WiFiDevicesViewSet,
        name='wifi-device-list',
    )
]

# add shutdown and restart
urlpatterns += [
    url(
        r'^restart-device/$', restart_device, name='restart-device',
    ),
    url(
        r'^restart-iotd/$',
        restart_iotd,
        name='restart-iotd',
    ),
    url(
        r'^shutdown-device/$',
        shutdown_device,
        name='shutdown-device',
    )
]

# chart
urlpatterns += [
    url(r'^dns-chart-data/$', DNSQueryChartData.as_view(),
        name='dns-chart-data'),
    url(r'^dns-table-data/$',
        DNSQueryTableData.as_view({'get': 'list'}), name='dns-table-data')
]
