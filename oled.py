### gonna try later when we have concentration and frequency 
import ssd1306
from machine import Pin, I2C
class OLED:
    def __init__(self, SCL_pin, SDA_pin):
        self.i2c = I2C(scl=Pin(SCL_pin), sda=Pin(SDA_pin), freq=400000)
        self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.oled.fill(0)
    
    def display_PID_controls(self, temperature,concentration,time):
        self.oled.fill(0)
        self.oled.text('Temp: ' + str(temperature), 0, 0)
        self.oled.text('Conc.: ' + str(concentration), 0, 8)
        #self.oled.text('Freq C.: ' + str(frequency), 0, 16)
        self.oled.text(str(time), 0, 16)
        
        self.oled.show()
        
        