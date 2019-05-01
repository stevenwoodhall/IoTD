#!/usr/bin/env bash
# IoTD: Installer Script
# https://github.com/z7ev3n/IoTD
#
# To install run to next line
# curl -L https://git.io/iotd | bash
#

## Script Variables ##
gitRepo="https://github.com/z7ev3n/IoTD.git"

## Parse Command Line Options
# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -s|--ssid)
    SSID="$2"
    shift # past argument
    shift # past value
    ;;
    -w|--passphrase)
    PASSPHRASE="$2"
    shift # past argument
    shift # past value
    ;;
    -u|--username)
    USERNAME="$2"
    shift # past argument
    shift # past value
    ;;
    -p|--password)
    PASSWORD="$2"
    shift # past argument
    shift # past value
    ;;
    --quiet)
    QUIET=1
    shift # past argument
    ;;
    --demo)
    DEMO=1
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Menu
display_info() {
  if [[ -z "${TERM}" ]]; then
    columns="$(tput cols)"
    TERM=ansi whiptail --title "$1" --infobox "$2" 20 $columns
  else
    echo "$1 - $2"
  fi
}

# Install Function for Raspberry Pi
install_pi() {
  sudo apt-get update -y -qq
  sudo apt-get install -y -qq git python3 python3-pip dnsmasq hostapd dnsutils jq nginx wbritish iptables dhcpcd5 wget
  sudo git clone $gitRepo "/opt/iotd"
  sudo chown -R pi:pi /opt/iotd
  mkdir -p /opt/iotd/app/dns/hosts-blocklists/
  wget https://raw.githubusercontent.com/notracking/hosts-blocklists/master/hostnames.txt -O /opt/iotd/app/dns/hosts-blocklists/hostnames.txt
  wget https://raw.githubusercontent.com/notracking/hosts-blocklists/master/domains.txt -O /opt/iotd/app/dns/hosts-blocklists/domains.txt
  # Generate Passwords
  # https://www.hughgrigg.com/posts/random-memorable-passwords-bash/
  if [ -z ${SSID+x} ]; then wifiSSID="IoTD"; else wifiSSID=$SSID; fi
  if [ -z ${PASSPHRASE+x} ]; then
    wifiPassword=$(shuf -n 3 /usr/share/dict/british-english | sed "s/./\u&/" | tr -cd "[A-Za-z]"; echo $(shuf -i0-999 -n 1));
  else
    wifiPassword=$PASSPHRASE;
  fi
  if [ -z ${USERNAME+x} ]; then
    userName=$(shuf -n 1 /usr/share/dict/british-english | sed "s/./\u&/" | tr -cd "[A-Za-z]"; echo $(shuf -i0-999 -n 1));
  else
    userName=$USERNAME;
  fi
  if [ -z ${PASSWORD+x} ]; then
    userPassword=$(shuf -n 3 /usr/share/dict/british-english | sed "s/./\u&/" | tr -cd "[A-Za-z]"; echo $(shuf -i0-999 -n 1));
  else
    userPassword=$PASSWORD;
  fi
  # Setup dhcpcd
sudo tee -a /etc/dhcpcd.conf << 'EOF'
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
  sudo service dhcpcd restart
  # Setup dnsmasq
  sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo tee -a /etc/dnsmasq.conf << 'EOF'
interface=wlan0 # Use the require wireless interface - usually wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
log-dhcp
log-queries
log-facility=/var/log/dnsmasq.log
# DNS Module
conf-file=/opt/iotd/app/dns/hosts-blocklists/domains.txt
addn-hosts=/opt/iotd/app/dns/hosts-blocklists/hostnames.txt
EOF
  sudo systemctl restart dnsmasq.service
  # Setup hostapd
sudo bash -c 'cat << EOF > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=IoTD
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=WelcomeToTheInternetOfThings
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF'
  sudo sed -i "s/\#DAEMON_CONF\=\"\"/DAEMON_CONF\=\"\/etc\/hostapd\/hostapd.conf\"/g" /etc/default/hostapd
  sudo sed -i '/ssid=/c\ssid='$wifiSSID /etc/hostapd/hostapd.conf
  sudo sed -i '/wpa_passphrase/c\wpa_passphrase='$wifiPassword /etc/hostapd/hostapd.conf
  sudo systemctl unmask hostapd.service
  sudo systemctl daemon-reload
  sudo systemctl enable hostapd
  sudo systemctl start hostapd dnsmasq
  # Setup network
  sudo sed -i "s/\#net.ipv4.ip_forward\=1/net.ipv4.ip_forward\=1/g" /etc/sysctl.conf
  sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
  sudo sed -i "s/exit 0/iptables-restore \< \/etc\/iptables\.ipv4\.nat\nexit 0/g" /etc/rc.local
  # Setup Python
  cd /opt/iotd
  find ./ -type f -name "requirements.txt" -exec sudo pip3 install -q -r "{}" \;
  # Install all dependencies
  for i in $(find -name "_iot_module_.json"); do
      jq '.reqirements.pip | to_entries[] | "\(.value)"' "$i" | xargs sudo pip3 install -q
      jq '.reqirements.packages | to_entries[] | "\(.value)"' "$i" | xargs sudo apt-get -qq install -y
  done
  # Setup nginx
  sudo mkdir /etc/nginx/ssl
  if [ ! -f /etc/nginx/ssl/nginx.key ]; then
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt -subj "/C=GB/ST=London/L=London/O=IOTD/OU=IOTD/CN=iotd.iot"
  fi
  sudo cp /opt/iotd/services/nginx/nginx.conf /etc/nginx/nginx.conf
  sudo systemctl restart nginx
  sudo ln -s /usr/local/lib/python3.5/dist-packages/django/contrib/admin/static/admin/ /opt/iotd/app/static/
  sudo ln -s /usr/local/lib/python3.5/dist-packages/rest_framework/static/rest_framework/ /opt/iotd/app/static/
  # setup core modules
  echo "* * * * * /usr/bin/python3 /opt/iotd/services/iotd-discovery/iotd-discovery.py >> /tmp/iotd-discovery.log 2>&1" >> /tmp/devcronjob
  crontab /tmp/devcronjob
  rm /tmp/devcronjob
  # setup services
  sudo cp /opt/iotd/services/iotd-django.service /etc/systemd/system/iotd-django.service
  sudo cp /opt/iotd/services/iotd-dns/iotd-dns.service /etc/systemd/system/iotd-dns.service
  sudo cp /opt/iotd/services/iotd-pcap/iotd-pcap.service /etc/systemd/system/iotd-pcap.service
  sudo systemctl daemon-reload
  sudo systemctl restart hostapd.service
  sudo systemctl enable iotd-django.service iotd-dns.service iotd-pcap.service
  sudo chmod +x /opt/iotd/services/iotd-pcap/rotate.sh
}

display_info "IoTD Installer" "IoTD will now start installing."
install_pi 2> /tmp/iotd_err.log

cd /opt/iotd/app
sudo chown -R pi:pi /opt/iotd
python3 -c 'import random; print ("SECRET_KEY="+"".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))' > /opt/iotd/.env
python3 manage.py makemigrations --no-input 2> /dev/null
python3 manage.py migrate --no-input 2> /dev/null
python3 manage.py migrate --run-syncdb --no-input 2> /dev/null

if [[ "$DEMO" == 1 ]]; then
  display_info "IoTD Installer" "Adding Demo Data"
  python3 manage.py flush --no-input 2> /dev/null
  python3 manage.py runscript add_demo_data 2> /dev/null
  sudo chown -R pi:pi /opt/iotd
  userName="demo"
  userPassword="demo"
else
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('$userName', 'admin@iotd.cloud', '$userPassword')" | python3 manage.py shell
  echo "from manager.models import Settings; s = Settings(wifi_ssid='$wifiSSID', wifi_password='$wifiPassword'); s.save()" | python3 manage.py shell
fi

cd /opt/iotd/app
# generate API key for user
apiKey=$(echo "from rest_framework.authtoken.models import Token; from django.contrib.auth.models import User; u = User.objects.get(username='$userName'); t = Token.objects.create(user=u); t.save(); print(t);" | python3 manage.py shell)
echo "IOTD_API_TOKEN=$apiKey" >> /opt/iotd/.env
sudo chown -R pi:pi /opt/iotd
sudo systemctl start iotd-django.service iotd-dns.service iotd-pcap.service 2> /dev/null


display_info "IoTD Installer" "IoTD is now installed! \

--- IoTD Login Info ---
Site: https://$(hostname -I | awk '{print $1}')
Username: $userName
Password: $userPassword
--- IoTD Wi-Fi Creds ---
Wi-Fi SSID: $wifiSSID
Wi-Fi SSID: $wifiPassword
---
GitHub: https://github.com/z7ev3n/IoTD \
"
