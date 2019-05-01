#!/usr/bin/python
from datetime import datetime
from dotenv import load_dotenv
import os
import re
import requests
import select
import subprocess
import time
load_dotenv(dotenv_path="/opt/iotd/.env")

"""
This script go watch for new lines in dnsmasq.log and
adds any DNS queries to the IoTD database.
"""

# Script variables
SERVER_URL = 'http://127.0.0.1:8000/api/dns-query/'
DNSMASQ_LOG = '/var/log/dnsmasq.log'
REQUEST_HEADERS = {'Authorization': 'Token {}'.format(
    os.getenv("IOTD_API_TOKEN"))}

# Function to parse line in log file using regex


def parseLine(line):
    DNSMASQ_REGEX = re.compile(
        r"(.*?) dnsmasq\[.*?\]: query\[(.*?)\] (.*?) from (.*?)$")
    m = re.match(DNSMASQ_REGEX, line)
    dtObj = datetime.strptime(m.group(1), "%b %d %H:%M:%S").replace(
        year=datetime.today().year)
    dt = dtObj.strftime("%Y-%m-%dT%H:%M:%SZ")
    return {'datetime': dt, 'record': m.group(2), 'domain': m.group(3),
            'src': m.group(4)}

# Sends data to the IoTD API


def postToDB(url, data):
    r = requests.post(url, json=data, headers=REQUEST_HEADERS)
    print(r.text)


f = subprocess.Popen(['tail', '-n0', '-f', '/var/log/dnsmasq.log'],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

while True:
    if p.poll(1):
        try:
            line = str(f.stdout.readline().decode('ascii'))
            if 'query' in line:
                if '127.0.0.1' not in line:
                    data = parseLine(line)
                    postToDB(SERVER_URL, data)
        except Exception as e:
            print(e)
    time.sleep(1)
