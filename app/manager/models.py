from django.db import models
import uuid


class Category(models.Model):
    """
    Model representing a Category (e.g. Camera).
    """
    name = models.CharField(
        max_length=200, help_text="Enter the name of the Category.")
    icon = models.CharField(
        max_length=25, help_text="Font awesome icon name", null=True,
        blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Device(models.Model):
    """
    Model representing a Device (e.g. iphone).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular device")
    mac = models.CharField(max_length=200, help_text="MAC Address")
    title = models.CharField(
        max_length=200, help_text="Name", null=True, blank=True)
    icon = models.CharField(
        max_length=200, help_text="FontAwesome Icon",
        default='question-circle')
    ipv4 = models.CharField(
        max_length=200, help_text="IPv4 Address", null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/device/%i/" % self.id


class Settings(models.Model):
    id = models.CharField(primary_key=True, default='settings',
                          max_length=50,
                          help_text="Unique ID for this setting")
    wifi_ssid = models.CharField(
        max_length=50, help_text="The name of the WiFi Network.",
        default='IoT')
    wifi_password = models.CharField(
        max_length=50,
        help_text="The password that devices use to connect to IoTD.",
        default='WelcomeToTheIOT')
    prowl_api_key = models.CharField(
        max_length=200,
        help_text="Prowl API key for sending push notifications.",
        null=True, blank=True)
    shodan_api_key = models.CharField(
        max_length=200, help_text="Shodan API key.", null=True, blank=True)

    def __str__(self):
        return str(self.id)
