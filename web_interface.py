import network
import time  
WIFI_SSID = ""
WIFI_PASSWORD = ""

def connect_wifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

    #connect to the wifi network 
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)

    if not wifi.isconnected():
        print('Connecting...')
        timeout = 0 
        while (not wifi.isconnected() and timeout < 10):
            print(10 - timeout)
            timeout += 1 
            time.sleep(1) # dont know how long it needs to connect 

    if wifi.isconnected():
        print('Yay! Connected :)')    

    else:
        wifi.disconnect()
        print('\n Not able to connect :(')    
