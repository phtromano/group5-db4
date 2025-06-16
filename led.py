from machine import PWM,Pin
class LED:
    
    def __init__(self):
        self.led = Pin(21,Pin.OUT)
    
    def turn_on_led(self):
        self.led.on()
    
    def turn_off_led(self):
        self.led.off()