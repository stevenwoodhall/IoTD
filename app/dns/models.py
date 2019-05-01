from manager.models import Device
import uuid
from django.db import models
import string

"""
This file details the database models of the DNS Detective module for IoTD.
"""


class DNSQuery(models.Model):
    """
    Model representing a DNSQuery.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this query")
    datetime = models.DateTimeField(null=True, blank=True)
    record = models.CharField(
        max_length=15, help_text="DNS Record e.g. A", null=True, blank=True)
    domain = models.CharField(
        max_length=200, help_text="domain e.g. google.com", null=True,
        blank=True)
    src = models.CharField(
        max_length=200, help_text="device IP e.g. 192.168.4.5", null=True,
        blank=True)
    device = models.ManyToManyField(
        Device, help_text="Select a device for this query", blank=True)

    def __str__(self):
        try:
            return self.domain
        except:
            return self.id

    @property
    def records(self):
        lst = {field.name: getattr(self, field.name)
               for field in self.__class__._meta.fields
               if field.name.startswith('d')}
        return lst


class BlockedDomains(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this query")
    domain = models.CharField(
        max_length=200, help_text="domain e.g. google.com", null=True,
        blank=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.domain


class HiddenDomains(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this query")
    domain = models.CharField(
        max_length=200, help_text="domain e.g. google.com", null=True,
        blank=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
