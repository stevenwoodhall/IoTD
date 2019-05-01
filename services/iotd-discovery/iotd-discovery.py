#!/usr/bin/python
from datetime import datetime
from dotenv import load_dotenv
import json
import os
import requests
import subprocess
import time
load_dotenv(dotenv_path="/opt/iotd/.env")
"""
This script looks for new devices and tells the API when it finds some.
"""

SERVER_URL = 'http://127.0.0.1:8000/api/devices/'
DNSMASQ_LEASES = '/var/lib/misc/dnsmasq.leases'
REQUEST_HEADERS = {'Authorization': 'Token {}'.format(
    os.getenv("IOTD_API_TOKEN"))}


def get_DNS_lease(mac):
    dnsmasq_leases = open(DNSMASQ_LEASES, 'r').read().split('\n')
    connections = {}
    for lease in dnsmasq_leases:
        if len(lease) > 0:
            data = lease.split(' ')
            if data[1] == mac:
                return data
    return None


def parse(output):
    stations = []
    mac = None
    ctime = None

    for line in output.splitlines():
        line = line.decode('utf-8').strip()
        if line.startswith('Station'):
            mac = line.split()[1]
            if mac is not None:
                if get_DNS_lease(mac):
                    data = get_DNS_lease(mac)
                    if data[3] == '*':
                        devTitle = 'Unknown'
                    else:
                        devTitle = data[3]
                    stations.insert(
                        0, {'mac': mac, 'ipv4': data[2], 'title': devTitle})
                else:
                    stations.insert(
                        0, {'mac': mac, 'ipv4': None, 'title': 'Unknown'})

    return stations


# Query devices associated with hotspot
cmd = "/sbin/iw dev wlan0 station dump"
result = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
# Parse output
deviceList = parse(result.stdout)

# get list of existing devices
r = requests.get("{}?format=json".format(SERVER_URL), headers=REQUEST_HEADERS)
devices = json.loads(r.text)

# send to api
for data in deviceList:
    newDevice = True
    for existingDevice in devices:
        if existingDevice['mac'] == data['mac']:
            newDevice = False
    if newDevice:
        r = requests.post(SERVER_URL, json=data, headers=REQUEST_HEADERS)
        print(r.text)
