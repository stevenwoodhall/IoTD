from django.conf.urls.static import static
from django.conf import settings
"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import json
import os
urlpatterns = [
    path('admin/', admin.site.urls),
]

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

# Add urls from apps
urlpatterns += [
    path('', include('manager.urls'))
]
urlpatterns += [
    path('api/', include('api.urls'))
]

# add module urls if contain _iot_module_.json
moduleList = []
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name == '_iot_module_.json':
            fp = os.path.join(root, name)
            with open(fp) as json_file:
                data = json.load(json_file)
                if data['enabled']:
                    moduleList.insert(0, root.strip('./'))
                else:
                    dtt = data['title']
                    print("[.] Skipping disabled module: {}".format(dtt))

for modName in moduleList:
    try:
        urlpatterns += [
            path('', include(modName + '.urls'))
        ]
    except Exception as e:
        print("[!] Failed to load module. {}".format(e))

# Use static() to add url mapping to serve static files during development

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
