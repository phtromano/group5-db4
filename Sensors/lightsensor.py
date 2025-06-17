from machine import Pin, ADC
import time
import math

class LightSensor:
    def __init__(self):
    
        self.adc = ADC(Pin(26))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.reference = 1620
        self.RGBStrip = Pin(25, Pin.OUT)


    def intesity(self):
        self.RGBStrip.value(1)
        time.sleep(.2)
        intesity = []

        for _ in range(200):
            intesity.append(self.adc.read())
        self.RGBStrip.value(0)
        return sum(intesity)/200
    
    def OD_value(self):
        intesity = self.intesity()

        initial_OD = (-math.log10(intesity/self.reference))
        return initial_OD
    
    

