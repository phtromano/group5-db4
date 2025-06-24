from servo import Servo
import time

musselValve = Servo(27)
algaeValve = Servo(13) 

while True:
    print('Valve open')
    musselValve.set_angle(180)
    
    time.sleep(4)