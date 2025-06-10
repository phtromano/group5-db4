from machine import Pin

class fanCooler:
    def __init__(self, pinPower, pinFan):
        self.power = Pin(pinPower, Pin.OUT)
        self.fan = Pin(pinFan, Pin.OUT)

    def coolerOn(self):
        self.fan.value(1)
    
    def coolerOff(self):
        self.fan.value(0)

    def powerHigh(self):
        self.power.value(0)
    
    def powerLow(self):
        self.power.value(1)