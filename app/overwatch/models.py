# from manager.models import Device
from django.db import models
import uuid


class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID")
    title = models.CharField(max_length=200, help_text="Alert Title")
    desc = models.CharField(max_length=200, help_text="Alert Description")
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
    dismissed = models.DateTimeField(blank=True)

    def __str__(self):
        return str(self.title)


class Host(models.Model):
    last_update = models.DateTimeField(primary_key=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
    ip_str = models.CharField(max_length=200, help_text="IP Address")
    ports = models.TextField(null=True, help_text="IP Address")

    def __str__(self):
        return str(self.ip_str)
