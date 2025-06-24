import network
import time  
from umqtt.robust import MQTTClient
from fanCooler import fanCooler
from Sensors.temperaturesensor import TempSensor
from Sensors.lightsensor import LightSensor
from coolerpump import Pump
from PID import PID
from servo import Servo
from oled import OLED
import os
import gc
import sys
import utime
import datetime
from math import log

isRunning = True
cooler = fanCooler(33,15)
coolerpump = Pump(14,32,1000)
temp_sensor = TempSensor() 
musselValve = Servo(25)
algaeValve = Servo(12) 
oLed = OLED()

valve_status = {'mussel': 'closed', 'algae': 'closed'}

target_temp = 17.5
pid = PID(temp_sensor.read_temp(), target_temp)

pid.setP(0.8)   
pid.setI(0.03)
pid.setD(0.2)

with open('system_info.csv','w') as f:
    f.write('Datetime,Temperature,PID_Output,Pump_Speed,Route,OD,Concentration,mlOfFood\n')

COOLING_INTERVAL = 10 * 1000  # 10 seconds in ms
FEEDING_INTERVAL = 60 * 60 * 1000  #1 hour in ms
TEMP_AVG_SAMPLES = 10
COOLING_ROUTE = 'mussel'
FEEDING_ROUTE = 'algae'
VOLUME_OF_BUCKET = 4000  # mL 
CONC_MUSSEL_BUCKET = 3 * 1250
CONC_MUSSEL_BUCKET_AT_TIME = 0

WIFI_SSID = "Eris"
WIFI_PASSWORD = "12345678"


# create a random MQTT clientID 
random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id = bytes('client_'+str(random_num), 'utf-8')

# connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
# 
# To use a secure connection (encrypted) with TLS: 
#   set MQTTClient initializer parameter to "ssl=True"
#   Caveat: a secure connection uses about 9k bytes of the heap
#         (about 1/4 of the micropython heap on the ESP8266 platform)
ADAFRUIT_IO_URL = b'io.adafruit.com' 
ADAFRUIT_USERNAME = b'erisandersen'
ADAFRUIT_IO_KEY = b'nhacoma'

SYSTEMRUNNING_FEED = 'System'
TEMPERATURE_FEED = 'Temperature'
OD_FEED = 'OD'
ROUTE_FEED = 'Route'
CONCETRATION_FEED = 'Concentration'
ALGAEVALVE_FEED = 'AlgaeValve'
MUSSELVALVE_FEED = 'MusselValve'

system_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, SYSTEMRUNNING_FEED), 'utf-8')
temperature_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TEMPERATURE_FEED), 'utf-8')
od_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, OD_FEED), 'utf-8')
route_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ROUTE_FEED), 'utf-8')
conc_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, CONCETRATION_FEED), 'utf-8')
algaevalve_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ALGAEVALVE_FEED), 'utf-8')
musselvalve_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, MUSSELVALVE_FEED), 'utf-8')

def call_back(topic, message):
    global isRunning
    print('Received Data:  Topic = {}, Message = {}'.format(topic, message))
    recieved_data = str(message, 'utf-8')   
    if recieved_data == "1":
        isRunning = False

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


def set_route(route):
    if route == 'mussel':
        musselValve.set_angle(180)  
        algaeValve.set_angle(90) 
        valve_status['mussel'] = 'open'
        valve_status['algae'] = 'closed'   
    elif route == 'algae':
        musselValve.set_angle(90)   
        algaeValve.set_angle(180)   
        valve_status['mussel'] = 'closed'
        valve_status['algae'] = 'open'


def adjustSpeedCooler(u):
    if u>2:
        cooler.coolerOn()
        cooler.powerHigh()
        coolerpump.setDirection(1)
        coolerpump.setSpeed(int(100*u))
    elif u<2 and u>0:
        cooler.coolerOn()
        cooler.powerLow()
        coolerpump.setDirection(1)
        coolerpump.setSpeed(1)
    elif u==0:
        cooler.coolerOff()
        coolerpump.setDirection(0)

def get_OD_and_concentration():
    #OD from RGB sensor
    r, g, b, c = rgb_sensor.read(True)  # You may need to adapt this line to your sensor's API
    
    OD = compute_OD(r, g, b, c)         # Replace with actual function
    concentration = compute_conc(OD)    # Replace with actual function
    return OD, concentration

def compute_mlOfFood(concentration, conc_mussel_bucket=CONC_MUSSEL_BUCKET, conc_mussel_bucket_at_time=CONC_MUSSEL_BUCKET_AT_TIME):
    
    try:
        ml = -VOLUME_OF_BUCKET * (conc_mussel_bucket_at_time - conc_mussel_bucket) / (concentration - conc_mussel_bucket)
    except ZeroDivisionError:
        ml = 0
    return ml

def send_data(temperature,OD,route_status,conc):
    try:
        client.publish(temperature_feed, bytes(str(temperature), 'utf-8'), qos=0)
        client.publish(od_feed, bytes(str(OD), 'utf-8'), qos=0)
        client.publish(route_feed, bytes(str(route_status), 'utf-8'), qos=0)
        client.publish(conc_feed, bytes(str(conc), 'utf-8'), qos=0)
        client.publish(algaevalve_feed, bytes(valve_status['algae'], 'utf-8'), qos=0)
        client.publish(musselvalve_feed, bytes(valve_status['mussel'], 'utf-8'), qos=0)
        
        print("\nTemp - ", str(temperature))
        print("\nOD - ", str(OD))
        print("\nCurrent Route - ", str(route_status))
        print("\nConcentration - ", str(conc))
        print("\nAlgaeValve - ", str(valve_status['algae']))
        print("\nMusselValve - ", str(valve_status['mussel']))

        print('Data sent')
        

    except:
        client.disconnect()
        print("\nDisconnected from the server, activities will run locally\n")

def average_temperature(temp_sensor):
    #its gonna take the average of 10 temperature measurements
    temperatures = [] 
    for _ in range(10):
        temperatures.append(temp_sensor.read_temp())
    newTemp = sum(temperatures)/10 - 1 
    return newTemp


connect_wifi()

client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)
try:            
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    client.disconnect()
    sys.exit()

client.set_callback(call_back)
client.subscribe(system_feed)


# publish free heap statistics to Adafruit IO using MQTT
#
# format of feed name:  
#   "ADAFRUIT_USERNAME/feeds/ADAFRUIT_IO_FEEDNAME"


##Start of main loop
current_route = COOLING_ROUTE
set_route(current_route)
last_cooling_time = utime.ticks_ms()
last_feeding_time = utime.ticks_ms()
PUBLISH_PERIOD_IN_SEC = 10 
while isRunning==True:
    newtemp = average_temperature(temp_sensor)
    u = PID.PID_values(newtemp)
    t0 = datetime.datetime.now()

    OD, concentration = get_OD_and_concentration()
    mlOfFood = compute_mlOfFood(concentration)

    try:
        client.check_msg()
    except:
        client.disconnect()
        print("\nDisconnected from the server, activities will run locally\n")

    # Every 10 sec
    # Cooling control
    if (utime.ticks_diff(utime.ticks_ms(),last_cooling_time) >= COOLING_INTERVAL): #10000 is 10s
        if current_route != COOLING_ROUTE:
            set_route(COOLING_ROUTE)
            current_route = COOLING_ROUTE
        adjustSpeedCooler(u)
        last_cooling_time = utime.ticks_ms()
        route = 'mussel'
        print(f"[{t0}] COOLING | T={newtemp:.2f} | u={u:.2f} | OD={OD:.2f} | Conc={concentration:.2f}")

        with open('system_info.csv','a') as f:
            f.write(f"{t0},{newtemp:.2f},{u:.2f},{coolerpump._speed},{route},{OD:.2f},{concentration:.2f},{mlOfFood:.2f}\n")

        send_data(newtemp,OD,current_route,concentration)
        oLed.display_PID_controls(newtemp, concentration, OD, str(t0)) 


    # Feeding control
    # Every feeding interval
    if (utime.ticks_diff(utime.ticks_ms(), last_feeding_time) >= FEEDING_INTERVAL):
        set_route(FEEDING_ROUTE)
        current_route = FEEDING_ROUTE
        print(f"[{t0}] FEEDING ALGAE | T={newtemp:.2f} | mL Food={mlOfFood:.2f}")

        with open('system_info.csv', 'a') as f:
                f.write(f"{t0},{newtemp:.2f},{u:.2f},{coolerpump._speed},algae,{OD:.2f},{concentration:.2f},{mlOfFood:.2f}\n")
        
        coolerpump.setDirection(1)
        coolerpump.setSpeed(100)  # Adjust speed for feeding    
        time.sleep(10)  # Feed for 10 seconds

        set_route(COOLING_ROUTE)
        current_route = COOLING_ROUTE
        last_feeding_time = utime.ticks_ms()
    utime.sleep_ms(200) 



cooler.coolerOff()
coolerpump.setDirection(0)
print("System stopped")

