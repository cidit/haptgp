
from reaktiv import Effect, Signal
import asyncio


import board
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle
from adafruit_gc9a01a import GC9A01A


def produce_display():
        
    spi = board.SPI()
    tft_cs = board.D8
    tft_dc = board.D25
    tft_reset = board.D27

    displayio.release_displays()
    
    
    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
    return GC9A01A(display_bus, width=240, height=240)

    

def app():
    route = Signal("menu/main")
    weather = Signal(
        {
            "temperature_C": 0,
            "humidity_%": 0,
            "lightlevel_lux": 0,
            "pressure_kPa": 0,
        }
    )
    
    display = produce_display()
    
    # Make the display context
    main_group = displayio.Group()
    display.root_group = main_group

    # _render_effect = Effect(lambda: render_task())
    _read_sensors = Effect(lambda: 0)
    
    Effect()