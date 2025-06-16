from machine import I2C, Pin
import time

class Si1145:
    """
    MicroPython driver for Si1145/46/47 proximity, UV index, and ambient light sensor.

    Usage:
        i2c = I2C(scl=Pin(22), sda=Pin(21))
        sensor = Si1145(i2c)
        sensor.reset()
        uv = sensor.read_uv_index()
        ambient = sensor.read_ambient()
        prox = sensor.read_proximity()
    """
    # I2C address
    ADDRESS = 0x60

    # Registers
    REG_PART_ID = 0x00
    REG_HW_KEY = 0x07
    REG_MEAS_RATE0 = 0x08
    REG_MEAS_RATE1 = 0x09
    REG_COMMAND = 0x18
    REG_RESPONSE = 0x20
    REG_IRQ_STATUS = 0x21
    REG_ALS_VIS_DATA0 = 0x22
    REG_ALS_VIS_DATA1 = 0x23
    REG_ALS_IR_DATA0  = 0x24
    REG_ALS_IR_DATA1  = 0x25
    REG_PS1_DATA0     = 0x26
    REG_PS1_DATA1     = 0x27
    REG_AUX_DATA0     = 0x2C
    REG_AUX_DATA1     = 0x2D
    REG_PARAM_WR      = 0x17
    REG_PARAM_RD      = 0x2E

    # Commands
    CMD_NOP        = 0x00
    CMD_RESET      = 0x01
    CMD_PS_FORCE   = 0x05
    CMD_ALS_FORCE  = 0x06
    CMD_PSALS_FORCE= 0x07

    # Parameter RAM addresses
    PARAM_CHLIST     = 0x01
    PARAM_PSLED12_SELECT = 0x02
    PARAM_PSLED3_SELECT  = 0x03

    def __init__(self, i2c, addr=ADDRESS):
        self.i2c = i2c
        self.addr = addr

    def write8(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value & 0xFF]))

    def read8(self, reg):
        return int.from_bytes(self.i2c.readfrom_mem(self.addr, reg, 1), 'little')

    def read16(self, reg_lsb):
        data = self.i2c.readfrom_mem(self.addr, reg_lsb, 2)
        return data[0] | (data[1] << 8)

    def reset(self):
        # Software reset sequence
        self.write8(self.REG_HW_KEY, 0x17)
        time.sleep_ms(10)
        # Enable UV, ALS, and PS1 in CHLIST
        # CHLIST: bit0 PS1, bit4 ALS_VIS, bit5 ALS_IR, bit6 AUX (UV)
        chlist = (1<<0) | (1<<4) | (1<<5) | (1<<6)
        self.param_write(self.PARAM_CHLIST, chlist)
        # Select LED1 for proximity
        self.param_write(self.PARAM_PSLED12_SELECT, 0x01)  # LED1
        self.param_write(self.PARAM_PSLED3_SELECT, 0x00)

    def param_write(self, param, value):
        self.write8(self.REG_PARAM_WR, value)
        self.write8(self.REG_COMMAND, 0xA0 | (param & 0x1F))  # PARAM_SET
        # Wait for command
        while (self.read8(self.REG_RESPONSE) & 0xF0) != 0:
            time.sleep_ms(1)

    def force_measure(self):
        # Force ALS and PS
        self.write8(self.REG_COMMAND, self.CMD_PSALS_FORCE)
        # wait for completion (RSP increment)
        prev = self.read8(self.REG_RESPONSE) & 0x0F
        while True:
            rsp = self.read8(self.REG_RESPONSE) & 0x0F
            if rsp != prev:
                break
            time.sleep_ms(1)

    def read_ambient(self):
        # Trigger forced ALS
        self.write8(self.REG_COMMAND, self.CMD_ALS_FORCE)
        time.sleep_ms(100)
        return self.read16(self.REG_ALS_VIS_DATA0), self.read16(self.REG_ALS_IR_DATA0)

    def read_proximity(self):
        # Trigger forced PS
        self.write8(self.REG_COMMAND, self.CMD_PS_FORCE)
        time.sleep_ms(50)
        return self.read16(self.REG_PS1_DATA0)

    def read_uv_index(self):
        # AUX returns UV*100
        self.write8(self.REG_COMMAND, self.CMD_PSALS_FORCE)
        time.sleep_ms(100)
        raw = self.read16(self.REG_AUX_DATA0)
        return raw / 100.0  # UV index
    


# if __name__ == '__main__':
# i2c = I2C(1, scl=Pin(22), sda=Pin(21))
# sensor = Si1145(i2c)
# sensor.reset()
# while True:
#     uv = sensor.read_uv_index()
#     vis, ir = sensor.read_ambient()
#     prox = sensor.read_proximity()
#     print('UV:', uv, 'Vis:', vis, 'IR:', ir, 'Prox:', prox)
#     time.sleep(1)
