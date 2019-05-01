# IoT Defender (IoTD)

![IoTD Screenshot](https://user-images.githubusercontent.com/1827161/57136168-dad50080-6da3-11e9-8344-eb614be99b5d.png)

IoTD is an application designed to your protect IoT devices, it runs on a Raspberry Pi and was developed as part of my final year project for university.

## About

IoTD creates its own Wi-Fi network for IoT devices to connect to and has a web inteface for monitoring and securing IoT devices.

![IoTD Design Diagram](https://user-images.githubusercontent.com/1827161/56987862-7db03380-6b86-11e9-9237-374ddc547c1a.png)

## Getting Started

Detailed instructions on installing and using IoTD can be found in the projects [wiki](https://github.com/z7ev3n/IoTD/wiki/Getting-Started).

### Installing

The installation of IoTD is automated, all you need to do is run the installer script by running the below code snippet on your Raspberry Pi.

```
curl -L https://git.io/iotd | bash
```

## Built With

* [Django](https://github.com/django/django) - The web framework for perfectionists with deadlines
* [Dnsmasq](http://thekelleys.org.uk/dnsmasq/doc.html) - Local DNS server
* [hostapd](https://w1.fi/hostapd/) - Used for Wi-Fi hotspot
* [Python 3](https://github.com/python/cpython) - The Python programming language
* [tcpdump](https://github.com/the-tcpdump-group/tcpdump) - The TCPdump network dissector

## Authors

* **Steven Woodhall** - [z7ev3n](https://github.com/z7ev3n)

## License

This project is licensed under the GNU General Public License v3.0 - see the
 [LICENSE.md](LICENSE.md) file for details.
