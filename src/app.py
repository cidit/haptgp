from reaktiv import Effect, Signal, Computed, LinkedSignal, batch
import asyncio

import time
import board

# import displayio
# import terminalio
# from adafruit_display_text.bitmap_label import Label
# from fourwire import FourWire
# from vectorio import Circle
# from adafruit_gc9a01a import GC9A01A
from adafruit_veml7700 import VEML7700
from adafruit_bme280.advanced import (
    Adafruit_BME280_I2C,
    MODE_FORCE,
    OVERSCAN_X1,
    MODE_NORMAL,
)
import sensors as s
from calib import get_latest_calibration


# def produce_display():
#     spi = board.SPI()
#     tft_cs = board.D8
#     tft_dc = board.D25
#     tft_reset = board.D27
#     displayio.release_displays()
#     display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
#     return GC9A01A(display_bus, width=240, height=240)

last = time.monotonic_ns() / 10**9


def angular_dist(from_angle, to_angle):
    if to_angle > from_angle:
        return from_angle-to_angle
    return to_angle-from_angle


def app():
    print("log: establishing coms")

    i2c = board.I2C()
    veml7700 = VEML7700(i2c)
    bme280 = Adafruit_BME280_I2C(i2c, 0x76)
    bme280.mode = MODE_NORMAL
    bme280.overscan_humidity = OVERSCAN_X1
    bme280.overscan_pressure = OVERSCAN_X1
    bme280.overscan_temperature = OVERSCAN_X1

    enco = s.RotaryEncoder()
    light = s.Light(veml7700, calibration=get_latest_calibration("light"))
    temperature = s.Temperature(bme280)
    humidity = s.Humidity(bme280)
    pressure = s.Pressure(bme280)

    # route = Signal("menu/main")

    def log_effect_fn():
        global last
        now = time.monotonic_ns() / 10**9
        dt = now - last
        last = now

        d = f"{dt * 1000:.2f}".rjust(8, "_")
        e = f"{enco.value() or 0.0:.2f}".rjust(8, "_")
        L = f"{light.value() or 0.0:.2f}".rjust(8, "_")
        t = f"{temperature.value() or 0.0:.2f}".rjust(8, "_")
        h = f"{humidity.value() or 0.0:.2f}".rjust(8, "_")
        p = f"{pressure.value() or 0.0:.2f}".rjust(8, "_")
        print(f"d:{d}ms\te:{e}deg\tl:{L}lux\tt:{t}C\th:{h}%\tp:{p}Pa")

    _log_effect = Effect(log_effect_fn)



    # rotated = LinkedSignal()

    # display = produce_display()

    # Make the display context
    # main_group = displayio.Group()
    # display.root_group = main_group


    """Setup of polling coroutines"""

    async def sensor_polling_fn(
        sensors: list[s.SensorReader],
        sleep=0.1,  # s
    ):
        while True:
            with batch():
                for sensor in sensors:
                    sensor.update()
            await asyncio.sleep(sleep)
            
    loop = asyncio.get_event_loop()

    sensor_polling = loop.create_task(
        sensor_polling_fn(
            [
                enco,
                light,
            ],
            sleep=1 / 50,
        )
    )
    bme280_polling = loop.create_task(
        sensor_polling_fn(
            [
                temperature,
                humidity,
                pressure,
            ],
            sleep=1 / 20,
        )
    )
    
    # TODO: thingsboard task and event handling
    try:
        tasks = asyncio.gather(
            sensor_polling,
            bme280_polling,
        )
        loop.run_until_complete(tasks)
    except asyncio.CancelledError:
        pass
