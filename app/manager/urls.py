from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^apps/$', views.apps, name='apps'),
    url(r'^devices/$', views.DeviceListView, name='devices'),
    url(r'^lookup-device/$', views.lookup_device, name='lookup-device'),
    url(r'^delete-device/$', views.delete_device, name='delete-device'),
    url(r'^device/(?P<pk>[0-9a-f-]+)/$',
        views.device_detail_view, name='device')
]


handler404 = views.handler404
handler500 = views.handler500
