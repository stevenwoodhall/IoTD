#!/usr/bin/env bash

LATEST_FILE=$(ls -t /var/log/iotd-pcaps/*pcap | head -1)
PCAP_SIZE=$(stat -c '%s' $LATEST_FILE )
cd /opt/iotd/app
# Tell IoTD about the new pcap
/usr/bin/python3 manage.py runscript add_pcap --script-args "$LATEST_FILE" "$PCAP_SIZE"
