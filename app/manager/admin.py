from django.contrib import admin

# Register your models here.
from .models import (Category, Device, Settings)

admin.site.register(Category)
admin.site.register(Device)
admin.site.register(Settings)
