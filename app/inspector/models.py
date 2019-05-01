from manager.models import Device
from django.db import models
import uuid
from os import path


class PacketCapture(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, help_text="Unique ID")
    dt_start = models.DateTimeField(blank=True)
    dt_end = models.DateTimeField(auto_now_add=True, blank=True)
    file_path = models.CharField(max_length=200, null=True, blank=True)
    file_size = models.CharField(max_length=25, null=True, blank=True)

    def filename(self):
        return str(path.basename(self.file_path))

    def __str__(self):
        return str(self.id)
