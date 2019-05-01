from django.contrib import admin

# Register your models here.
from .models import (BlockedDomains, DNSQuery, HiddenDomains)

admin.site.register(BlockedDomains)
admin.site.register(DNSQuery)
