from coolerpump import Pump
from fanCooler import fanCooler
from servo import Servo
import time


coolerpump = Pump(14,32,1000)
musselValve = Servo(25)
algaeValve = Servo(12) 

t0 = time.time()
while True:
    musselValve.set_angle(90)
    algaeValve.set_angle(180)
    coolerpump.setDirection(1)
    coolerpump.setSpeed(5000)
    print(time.time()-t0,"s")
    time.sleep(1)


