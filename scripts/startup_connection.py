# https://docs.circuitpython.org/projects/gc9a01a/en/latest/
# https://docs.circuitpython.org/projects/displayio-layout/en/latest/examples.html#switch-simple-test
# https://docs.circuitpython.org/projects/color_terminal/en/latest/

"""testing status:
- [X] verified working
"""

import board
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle
import subprocess
# import board
import busio
import cst816
from adafruit_gc9a01a import GC9A01A
import time
import random
from smbus2 import SMBus

time.sleep(5)

# Initialize I2C
i2c = busio.I2C(3, 2)
touch = cst816.CST816(i2c)

tft_cs = board.D8
tft_dc = board.D25
tft_reset = board.D27

spi = board.SPI()

displayio.release_displays()

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = GC9A01A(display_bus, width=240, height=240)

# Make the display context
main_group = displayio.Group()
display.root_group = main_group

bg_bitmap = displayio.Bitmap(240, 240, 2)
color_palette = displayio.Palette(6)
color_palette[0] = 0x00FF00  # Bright Green
color_palette[1] = 0xAA0000  # Red
color_palette[2] = 0x786452 
color_palette[3] = 0x443730  
color_palette[4] = 0xA5907E  
color_palette[5] = 0xF7DAD9  

bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

inner_circle = Circle(pixel_shader=color_palette, x=120, y=120, radius=100, 
                    #   color_index=1
                      )
main_group.append(inner_circle)

# Draw a label
text_group = displayio.Group(scale=1, x=25, y=90)


ip = subprocess.check_output(["hostname -I"], shell=True).decode().strip()
ssid = subprocess.check_output(["nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2"], shell=True).decode()
# .split(":")[1].replace('"', '')



print(ip)
print(ssid)

text_area = Label(terminalio.FONT, text=f"ssid:{ssid}\n{ip}", color=0xFF0000, line_spacing=0.5)
uptime_grp = displayio.Group(scale=1, x=0, y=30)
uptime_txt_area = Label(terminalio.FONT, color=0x000)
uptime_grp.append(uptime_txt_area)

text_group.append(text_area)
text_group.append(uptime_grp)
main_group.append(text_group)



# Define I2C bus number (e.g., 1 for Raspberry Pi 2/3/4)
I2C_BUS_NUMBER = 1
# Define the I2C address of your slave device (e.g., from i2cdetect)
DEVICE_ADDRESS = 0x06   # Example: MT6701 address
# Define the register address within the device to read/write
REGISTER_DIR = 0x29 #DIR = 1 for CW (bit 1)
REGISTER_ANGLE_MSB = 0x03   # Angle<13:6>
REGISTER_ANGLE_LSB = 0x04   # Angle<5:0>


#Ce type de filtre ne fonctionne pas avec les angles (passage de 360 à 0 !!!!)
filtered_angle = 0
alpha = 0.1 # must be between 0 and 1 inclusive


def low_pass_filter(prev_value, new_value):
    return alpha * prev_value + (1 - alpha) * new_value

def get_angle():
    new_angle = None
    try:
        # Open the I2C bus
        with SMBus(I2C_BUS_NUMBER) as bus:
        
            # Read DIR REGISTER
            bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_DIR)
            #Set direction clockwise
            bytes1 = bytes1 |  0b00000010   #DIR = 1 for CW (bit 1)
            # Write DIR REGISTER
            bus.write_byte_data(DEVICE_ADDRESS, REGISTER_DIR, bytes1)
                
            #Read Angle MSB Register (Angle<13:6>) ... Bit7 to Bit0
            bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_MSB)
            #print(f"Read byte from register {hex(REGISTER_ADDRESS_MSB)}: {hex(bytes1)}")
        
            #Read Angle LSB Register (Angle<5:0>) ... Bit7 to Bit2
            bytes2 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_LSB)
            #print(f"Read byte from register {hex(REGISTER_ADDRESS_LSB)}: {hex(bytes2)}")
        
            # Concatenate bytes2 with bytes1
            angle_int = bytes2 >> 2
            angle_int = (bytes1 << 6) | angle_int 
        
            # Compute angle in degrees (14 bits)
            new_angle = angle_int * (360.0/16384.0)

            # print(f"Angle is: {new_angle:.0f}")
            print(f"Angle is: {new_angle:.0f}")
            
            #filtered_angle = low_pass_filter(filtered_angle, new_angle)
            #print(f"Angle is: {filtered_angle:.0f}")

    except FileNotFoundError:
        print(f"Error: I2C bus {I2C_BUS_NUMBER} not found. Ensure I2C is enabled.")
    except OSError as e:
        print(f"Error communicating with I2C device: {e}")
        print("Check device address, connections, and permissions.")
    return new_angle


while True:
    if touch.get_touch():
        inner_circle.color_index = random.randint(0, 5)
    uptime_txt_area.text = f"uptime: {round(time.monotonic(), 2)} angle: {get_angle()}"
    display.refresh()
