from machine import Pin, I2C
import tcs34725

class RGB_Sensor:
    def __init__(self):
        self.i2c = I2C(scl=Pin(22), sda=Pin(23), freq=400000)
        self.rgbsensor = tcs34725.TCS34725(self.i2c)
    
    def setGain(self, value):
        self.sensor.gain(value)
    
    def rgb_bytes(self, color):
        r,g,b,no_color = color

        if no_color == 0:
            return (0,0,0)
        red   = int(pow((int((r/no_color) * 256) / 255), 2.5) * 255)
        green = int(pow((int((g/no_color) * 256) / 255), 2.5) * 255)
        blue  = int(pow((int((b/no_color) * 256) / 255), 2.5) * 255)

        if red > 255:
            red = 255
        if green > 255:
            green = 255
        if blue > 255:
            blue = 255
        return (red, green, blue)
