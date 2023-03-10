import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = '*'
password = '*'

station = network.WLAN(network.STA_IF)

station.active(True)
# station.config(dhcp_hostname="Kerstboom")
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())
