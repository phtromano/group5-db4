from fanCooler import fanCooler
from Sensors.temperaturesensor import TempSensor

from coolerpump import Pump
from math import log
import utime
import time


cooler = fanCooler(33,15)
coolerpump = Pump(14,32,1000)
temp_sensor = TempSensor() 


total_seconds = 10*60               
interval = 5 

filename = "temperaturevsgrowth.csv"
with open(filename, "w") as f:
    f.write("time_s,temperature_C\n")  # CSV header

print("Starting cooling test.")



t0 = time.time()
for t in range(total_seconds):
    temp = temp_sensor.read_temp()
    elapsed = int(time.time() - t0)
    if temp > 17.5:
        cooler.coolerOn()
        cooler.powerHigh()
        coolerpump.setDirection(1)
        coolerpump.setSpeed(1000)
        print("Cooler on")
    elif temp <17.5:
        cooler.coolerOff()
        coolerpump.setDirection(0)
    
        print("Cooler off")
    with open(filename, "a") as f:
        f.write("{},{}\n".format(elapsed, temp))
    print("t = {}s, T = {:.2f}°C".format(elapsed, temp))
    utime.sleep(interval)

cooler.coolerOff()
coolerpump.setDirection(0)
coolerpump.setSpeed(1)
print("Cooling test complete.")
