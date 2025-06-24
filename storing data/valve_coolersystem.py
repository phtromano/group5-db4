from fanCooler import fanCooler
from coolerpump import Pump  
from servo import Servo
import time


cooler = fanCooler(33, 15)              
coolerpump = Pump(14, 32, 1000)
musselValve = Servo(25)
algaeValve = Servo(12) 

while True:
    print("mussel valve open")        
    musselValve.set_angle(180)
    algaeValve.set_angle(90)
    cooler.coolerOn()
    cooler.powerLow()
    coolerpump.setDirection(1)

    time.sleep(10)
    print("algae valve open")

    algaeValve.set_angle(180)
    musselValve.set_angle(90)
    time.sleep(1)
    cooler.coolerOn()
    cooler.powerLow()
    coolerpump.setDirection(1)
    time.sleep(10)




    