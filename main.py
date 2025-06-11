from machine import Pin,PWM
import time
#from fanCooler import fanCooler

#cooler = fanCooler(12,13)

#cooler.coolerOn()

from led import LED
light = LED()
#light = Pin(13,Pin.OUT)

while True:
    #light.on()
    light.turn_on_led()
    time.sleep(1)
    #light.off()
    light.turn_off_led()
    time.sleep(1)








