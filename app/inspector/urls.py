from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^inspector/$', views.inspector_summary, name='inspector'),
    url(r'^pcap/(?P<pk>[0-9a-f-]+)/$',
        views.inspector_capture, name='inspector-pcap')
]
