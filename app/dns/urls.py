from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^dns/$', views.test, name='test'),
    url(r'^clear-dns/$', views.clear_dns, name='clear-dns')

]
