from fanCooler import fanCooler
from Sensors.temperaturesensor import TempSensor
from coolerpump import Pump
from PID import PID
from servo import Servo
#from oled import OLED
from machine import I2C,PWM
from od import *               
from led_strip import *         
from tcs34725 import TCS34725   
from math import log
import utime
import time
from led_strip import *

isRunning=True
cooler = fanCooler(33,15)
coolerpump = Pump(14,32,1000)
temp_sensor = TempSensor() 
musselValve = Servo(27)
algaeValve = Servo(13) 
#oLed = OLED(22,23)

target_temp = 17.5
pid = PID(temp_sensor.read_temp(), target_temp)

pid.setP(0.8)   
pid.setI(0.03)
pid.setD(0.2)

try:
    f = open('system_info1.csv')
except OSError:
    with open('system_info1.csv','w') as f:
        f.write('Datetime,Temperature,PID_Output,Route,Concentration,mlOfFood\n')


COOLING_INTERVAL = 10 * 1000  # 10 seconds in ms
FEEDING_INTERVAL = 60000 #1 minutes in ms (adjust as needed)
TEMP_AVG_SAMPLES = 10
COOLING_ROUTE = 'mussel'
FEEDING_ROUTE = 'algae'
VOLUME_OF_BUCKET = 4000  # mL 
CONC_MUSSEL_BUCKET = 3 * 1250  #need to ask for the concentration
CONC_MUSSEL_BUCKET_AT_TIME = 0

def set_route(route):
    if route == 'mussel':
        musselValve.set_angle(180)  
        algaeValve.set_angle(105) 

    elif route == 'algae':
        musselValve.set_angle(107)   
        algaeValve.set_angle(180) 
 

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




def average_temperature(temp_sensor):
    #its gonna take the average of 10 temperature measurements
    temperatures = [] 
    for _ in range(10):
        temperatures.append(temp_sensor.read_temp())
    newTemp = sum(temperatures)/10 - 1 
    return newTemp


def compute_mlOfFood(concentration, conc_mussel_bucket=CONC_MUSSEL_BUCKET, conc_mussel_bucket_at_time=CONC_MUSSEL_BUCKET_AT_TIME):
    
    try:
        ml = -VOLUME_OF_BUCKET * (conc_mussel_bucket_at_time - conc_mussel_bucket) / (concentration - conc_mussel_bucket)
    except ZeroDivisionError:
        ml = 0
    return ml

def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

### Main loop start here
current_route = FEEDING_ROUTE
set_route(current_route)
last_cooling_time = utime.ticks_ms()
last_feeding_time = utime.ticks_ms()

print('System start.....')

t_start = time.ticks_ms()
t_between_od_measurements = 20000 #60s
number_of_samples_per_measurement = 15
N0 = 18000 #initial concentration of algae
rgb_measure = False
# **************************LED STRIP CONTOLL**************************************
R_PIN = 12
G_PIN = 25
B_PIN = 26
W_PIN = 21

led = RGBWLED(r_pin=R_PIN, g_pin=G_PIN, b_pin=B_PIN, w_pin=W_PIN)
led.set_brightness(0.5)
#Blue-Red Dominant (Balanced Growth)
r = 200
g = 0
b = 200
w = 255
led.set_color(r, g, b, w)
#TODO : turn off white led when taking the od measurement
#***********************************************************************************

#RGB SENSOR***************************************
i2c = I2C(1, scl=Pin(22), sda=Pin(23))
sensor = TCS34725(i2c)
sensor.integration_time(100.0) 
sensor.gain(16)                 # 1, 4, 16, or 60
#time of the first od reading
blue_channel = 0
c_channel = 0
#************************************************************************************

#KALMAN FILTER***********************************
R = 9e6
Q = 1e4
P0 = 6.4e7
kf = ScalarKalman(
x0=N0, P0=P0,
Q=Q, R=R,
growth_func=algae_growth_model,
jacobian_F=algae_growth_jacobian
)
#************************************************************************************

t_prev = time.ticks_ms()
sum_B = 0.0
sum_C = 0.0
count = 0

while isRunning==True:
    
    t_now = time.ticks_ms()
    # 1) start window every t_between_od_measurements
    if time.ticks_diff(t_now, t_prev) >= t_between_od_measurements:
        led.set_color(r, g, b, 0)
        rgb_measure = True

    # 2) collect samples
    if rgb_measure:
        raw = sensor.read(raw=True)
        #print(raw)
        sum_B += raw[2]
        sum_C += raw[3]
        count += 1
        time.sleep_ms(100)

        if count >= number_of_samples_per_measurement:
            mean_B = sum_B/count
            mean_C = sum_C/count

            # 3) compute dt and reset t_prev
            dt = time.ticks_diff(time.ticks_ms(), t_prev)
            t_prev = time.ticks_ms()

            # 4) fuse both channels
            z = bc_to_concentration(mean_B, mean_C)
            kz_B = blue_to_concentration(mean_B)
            kz_C = c_to_concentration(mean_C)

            kf.predict(dt)
            # kf.update(z)
            kf.update(kz_B, R=1.06e5)
            kf.update(kz_C, R=5.9e6)
            
            print(kz_B, kz_C, kf.x)
            #print(kf.x)

            # 5) reset for next window
            sum_B = sum_C = 0.0
            count = 0
            rgb_measure = False
            led.set_color(r, g, b, w)
    
    newtemp = average_temperature(temp_sensor)
    u = pid.PID_values(newtemp)
    if u > 0:
        u=pid.PID_values(newtemp)
    else:
        u=0
    t0 = time.time()
    timestamp = seconds_to_hms(t0)
    if kf.x <0:
        kf.x=0


    
    mlOfFood = compute_mlOfFood(kf.x)

    # Every 10 sec
    # Cooling control
    if (utime.ticks_diff(utime.ticks_ms(),last_cooling_time) >= COOLING_INTERVAL): #10000 is 10s
        if current_route != COOLING_ROUTE:
            set_route(COOLING_ROUTE)
            current_route = COOLING_ROUTE
        adjustSpeedCooler(u)
        last_cooling_time = utime.ticks_ms()
        route = 'mussel'
        print(f"[{timestamp}] COOLING | T={newtemp:.2f} | u={u:.2f} | Conc={kf.x:.2f}")

        with open('system_info1.csv','a') as f:
            f.write(f"{timestamp},{newtemp:.2f},{u:.2f},{route},{kf.x:.2f},{mlOfFood:.2f}\n")
            
        #oLed.display_PID_controls(newtemp, kf.x) 


    # Feeding control
    # Every feeding interval
    if (utime.ticks_diff(utime.ticks_ms(), last_feeding_time) >= FEEDING_INTERVAL):
        set_route(FEEDING_ROUTE)
        current_route = FEEDING_ROUTE
        print(f"[{timestamp}] FEEDING ALGAE | T={newtemp:.2f} | mL Food={mlOfFood:.2f}")

        with open('system_info1.csv', 'a') as f:
                f.write(f"{timestamp},{newtemp:.2f},{u:.2f},algae,{kf.x:.2f},{mlOfFood:.2f}\n")
        
        coolerpump.setDirection(1)
        coolerpump.setSpeed(100)  
        time.sleep(10)  # Feed for 10 seconds

        set_route(COOLING_ROUTE)
        current_route = COOLING_ROUTE
        last_feeding_time = utime.ticks_ms()
    utime.sleep_ms(200) 



cooler.coolerOff()
coolerpump.setDirection(0)
print("System stopped")