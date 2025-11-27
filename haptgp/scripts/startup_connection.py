"""
HOW TO USE
add the following line at the bottom of crontab (which you can edit with `crontab -e`)
@reboot $PROJDIR=<path to project from root> $USERHOME=<user home> $USERHOME/.local/bin/uv run --project $PROJDIR $PROJDIR/scripts/startup_connection.py > $USERHOME/corn.log 2>&1 
"""

import board
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
import subprocess
# import board
import busio
import cst816
from adafruit_gc9a01a import GC9A01A
import time
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

text_group = displayio.Group(scale=1, x=25, y=90)


ip = subprocess.check_output(["hostname -I"], shell=True).decode().strip()
ssid = subprocess.check_output(["nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2"], shell=True).decode()


print(ip)
print(ssid)

text_area = Label(terminalio.FONT, text=f"ssid:{ssid}\n{ip}", color=0xFFFFFF, line_spacing=0.5)
uptime_grp = displayio.Group(scale=1, x=0, y=30)
uptime_txt_area = Label(terminalio.FONT, color=0xFF0000)
uptime_grp.append(uptime_txt_area)

text_group.append(text_area)
text_group.append(uptime_grp)
main_group.append(text_group)



while True:
    if touch.get_touch():
        break
    print(time.monotonic(),"hello")
    uptime_txt_area.text = f"uptime: {round(time.monotonic(), 2):.2}"
    time.sleep(1/30)
