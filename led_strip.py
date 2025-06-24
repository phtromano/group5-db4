from machine import Pin, PWM

class RGBWLED:
    """
    Simple driver for a 4-pin RGBW LED strip using PWM on ESP32 with MicroPython.

    Usage:
        led = RGBWLED(r_pin=15, g_pin=2, b_pin=4, w_pin=16)
        led.set_color(128, 64, 255, 0)  # Set red=128, green=64, blue=255, white=0
        led.off()  # Turn off all channels
    """
    def __init__(self, r_pin, g_pin, b_pin, w_pin, freq=1000):
        # Initialize PWM for each color channel
        self.r = PWM(Pin(r_pin), freq=freq, duty_u16=0)
        self.g = PWM(Pin(g_pin), freq=freq, duty_u16=0)
        self.b = PWM(Pin(b_pin), freq=freq, duty_u16=0)
        self.w = PWM(Pin(w_pin), freq=freq, duty_u16=0)
        self._channels = (self.r, self.g, self.b, self.w)
    def _map_value(self, val):
        """
        Map an 8-bit value (0-255) to PWM duty (0-1023).
        """
        if val < 0:
            val = 0
        elif val > 255:
            val = 255
        return int(val * 1023 // 255)
    
    def set_brightness(self, level):
        """
        Set global brightness (0.0 to 1.0).
        """
        if level < 0:
            level = 0.0
        elif level > 1:
            level = 1.0
        self.brightness = level


    def set_color(self, r=0, g=0, b=0, w=0):
        """
        Set the color of the LED strip.

        Args:
            r (int): Red channel (0-255)
            g (int): Green channel (0-255)
            b (int): Blue channel (0-255)
            w (int): White channel (0-255)
        """
        r = int(r * self.brightness)
        g = int(g * self.brightness)
        b = int(b * self.brightness)
        w = int(w * self.brightness)

        self.r.duty_u16(self._map_value(r))
        self.g.duty_u16(self._map_value(g))
        self.b.duty_u16(self._map_value(b))
        self.w.duty_u16(self._map_value(w))
    def off(self):
        """
        Turn off all channels.
        """
        self.set_color(0, 0, 0, 0)