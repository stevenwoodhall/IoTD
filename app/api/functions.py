import re
from datetime import datetime
import pytz
import subprocess
import time

# converts epoch to datetime object


def convert_seconds_to_date(seconds):
    local_tz = pytz.timezone("Europe/London")
    epoch = int(time.time())
    timestamp = epoch - seconds
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    local_dt = local_tz.normalize(utc_dt.astimezone(local_tz))
    return local_dt.strftime("%m %b %Y %H:%M:%S")

# returns a list of connected Wi-Fi clients


def get_wifi_clients():
    result = {}
    try:
        clients = subprocess.run(
            ['iw', 'dev', 'wlan0', 'station', 'dump'], stdout=subprocess.PIPE)
        clients = clients.stdout.decode('ascii')
        for client in clients.split('Station')[1:]:
            lines = client.split('\n')
            mac = lines[0].strip().split()[0]
            result[mac] = {}
            for line in lines[1:]:
                if line:
                    key, value = line.split(':')
                    result[mac][key.strip().lower().replace(
                        ' ', '_')] = value.strip()
    except Exception as e:
        print(e)
    return result


# parse dnsmasq
def get_dns_data():
    def parseLine(line):
        DNSMASQ_REGEX = re.compile(
            r"(.*?) dnsmasq\[.*?\]: query\[(.*?)\] (.*?) from (.*?)$")
        m = re.match(DNSMASQ_REGEX, line)
        if m:
            dtObj = datetime.strptime(m.group(1), "%b %d %H:%M:%S").replace(
                year=datetime.today().year)
            dt = dtObj.strftime("%Y-%m-%dT%H:%M:%SZ")
            return {'datetime': dt, 'record': m.group(2), 'domain': m.group(3),
                    'src': m.group(4)}

    output = {'records': []}
    counter = 0
    cmd = "sudo cat /var/log/dnsmasq.log"
    result = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
    lines = result.stdout.decode('ascii').splitlines()
    for line in lines:
        if 'query' in line:
            if '127.0.0.1' not in line:
                data = parseLine(line)
                if data:
                    counter += 1
                    current = output['records']
                    current.append(data)
                    output['records'] = current

    output["queryRecordCount"] = counter
    output["totalRecordCount"] = counter

    return output
