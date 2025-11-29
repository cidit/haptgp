# https://docs.circuitpython.org/projects/veml7700/en/latest/

"""testing status:
- [X] verified working
"""

import time
import board
from adafruit_veml7700 import VEML7700

i2c = board.I2C()  # uses board.SCL and board.SDA
veml7700 = VEML7700(i2c)

while True:
    print("Ambient light:", veml7700.light)
    time.sleep(0.1)