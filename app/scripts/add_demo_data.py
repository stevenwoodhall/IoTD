# scripts/add_demo_data.py
from datetime import timedelta, date, datetime
from django.contrib.auth.models import User
from dns.models import DNSQuery
from manager.models import Device, Settings
from overwatch.models import Alert
from rest_framework.authtoken.models import Token
import random


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def run():
    # Create a Demo User
    user = User.objects.create_user(
        username='demo', email='demo@iotd.cloud', password='demo')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    Settings.objects.get_or_create(
        wifi_ssid='IoTD', wifi_password='WelcomeToTheInternetOfThings')
    # Register Devices
    Device.objects.bulk_create(
        [Device(title="Google Chromecast", mac='3c:5a:b4:b1:d7:ef',
                ipv4='192.168.4.28', icon='tv'),
         Device(title="TP-Link Smart Plug", mac='50:c7:bf:b1:d7:ef',
                ipv4='192.168.4.18', icon='plug'),
         Device(title="Netatmo Weather Station",
                mac='70:ee:50:37:10:c4', ipv4='192.168.4.15',
                icon='temperature-low'),
         Device(title="Xiaomi Xiaofang", mac='34:ce:00:f1:51:45',
                ipv4='192.168.4.29', icon='camera')
         ])
    # Create Historical DNS data
    data = []
    for d in daterange(date.today() - timedelta(30), date.today()):
        dt = datetime.fromordinal(d.toordinal())
        # Make between 50 and 100 requests
        # Google Chromecast
        for x in range(random.randint(0, 50)):
            data.append(DNSQuery(datetime=dt.replace(
                hour=random.randint(0, 23), minute=random.randint(0, 59),
                second=random.randint(0, 59)), domain=random.choice(
                ["android.clients.google.com", "clients3.google.com",
                 "mtalk.google.com", "time.google.com"]),
                src="192.168.4.28", record="A"))
        # TP-Link Smart Plug
        for x in range(random.randint(0, 50)):
            data.append(DNSQuery(datetime=dt.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59), second=random.randint(0, 59)),
                domain=random.choice(
                ["uk.pool.ntp.org", "time-b.nist.gov",
                 "s1a.time.edu.cn", "s1b.time.edu.cn"]),
                src="192.168.4.18", record="A"))
        # Netatmo Weather Station
        for x in range(random.randint(0, 50)):
            data.append(DNSQuery(datetime=dt.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59), second=random.randint(0, 59)),
                domain=random.choice(["netcom.netatmo.net"]),
                src="192.168.4.15", record="A"))
        # Xiaomi Xiaofang
        for x in range(random.randint(0, 50)):
            data.append(DNSQuery(datetime=dt.replace(
                hour=random.randint(0, 23), minute=random.randint(0, 59),
                second=random.randint(0, 59)),
                domain=random.choice(
                ["apicn.ismartalarm.com",
                 "clock.fmt.he.net", "t2.timegps.net", "ott.io.mi.com",
                 "ntp1.vniiftri.ru"]),
                src="192.168.4.29", record="A"))
    DNSQuery.objects.bulk_create(data)

    # Add Some Alerts
    Alert.objects.bulk_create(
        [Alert(title="🚨 Port 22 Open!", desc="Detected port 22/tcp (SSH)"
               " is open.", datetime=dt, dismissed=datetime.now()),
         Alert(title="🚨 Port 80 Open!", desc="Detected port 80/tcp (HTTP)"
               " is open.",
               datetime=dt, dismissed=datetime.now())
         ])
