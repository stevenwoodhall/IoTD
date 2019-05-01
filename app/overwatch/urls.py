from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^overwatch/$', views.overwatch_summary, name='overwatch')
]
