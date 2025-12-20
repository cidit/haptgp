from reaktiv import Computed, Effect, batch
import asyncio
import paho.mqtt.client as mqtt

import time
import board

import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle
from adafruit_gc9a01a import GC9A01A
import adafruit_ds3231
from adafruit_veml7700 import VEML7700
from adafruit_bme280.advanced import (
    Adafruit_BME280_I2C,
    MODE_FORCE,
    OVERSCAN_X1,
    MODE_NORMAL,
)

import cst816


import reaktiveui as rui
import sensors as s
from calib import get_latest_calibration
from cusinputs import KnobCtls
import views as v


def produce_display():
    """
    produces a display that does not auto refresh
    """
    spi = board.SPI()
    tft_cs = board.D8
    tft_dc = board.D25
    tft_reset = board.D27
    displayio.release_displays()
    display_bus = FourWire(
        spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset, baudrate=80_000_000
    )
    display = GC9A01A(display_bus, width=240, height=240)
    display.auto_refresh = False
    return display


def produce_mqtt(host):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = print
    mqttc.on_message = print
    mqttc.username_pw_set("haptgp-f", "haptgp-f")
    mqttc.connect(host)
    return mqttc


last = time.monotonic_ns() / 10**9


def app():
    """Sensor initialisation"""
    i2c = board.I2C()
    rtc = adafruit_ds3231.DS3231(i2c)
    veml7700 = VEML7700(i2c)
    bme280 = Adafruit_BME280_I2C(i2c, 0x76)
    bme280.mode = MODE_NORMAL
    bme280.overscan_humidity = OVERSCAN_X1
    bme280.overscan_pressure = OVERSCAN_X1
    bme280.overscan_temperature = OVERSCAN_X1

    """Signal definitions"""
    enco = s.RotaryEncoder()
    light = s.Light(veml7700, calibration=get_latest_calibration("light"))
    temperature = s.Temperature(bme280)
    humidity = s.Humidity(bme280)
    pressure = s.Pressure(bme280)

    knob = KnobCtls(
        enco.value,  # acts like a value getter, since its a signal
        time_constant_s=0.2,  # higher it is, the less jitter, but the more memory used and lower the responsiveness
        stopped_variator=20,  # higher means less jitter but longer minimum speed
    )

    @Effect
    def log_effect_fn():
        global last
        now = time.monotonic_ns() / 10**9
        dt = now - last
        last = now

        T = f"{dt * 1000:.2f}".rjust(8, "_")
        e = f"{enco.value() or 0.0:.2f}".rjust(8, "_")
        L = f"{light.value() or 0.0:.2f}".rjust(8, "_")
        t = f"{temperature.value() or 0.0:.2f}".rjust(8, "_")
        h = f"{humidity.value() or 0.0:.2f}".rjust(8, "_")
        p = f"{pressure.value() or 0.0:.2f}".rjust(8, "_")
        d = f"{knob.direction_just_changed()['actual']}".rjust(4, " ")
        s = f"{knob.speed._value or 0.0:.2f}".rjust(8, "_")

        print(f"{T}ms\te:{e}deg\tl:{L}lux\tt:{t}C\th:{h}%\tp:{p}Pa\tdir:{d}\tspd:{s}")

    """Screen handling"""

    routes = {
        "/summary": v.summary(
            temperature=temperature.value,
            enco=enco.value,
            humidity=humidity.value,
            light=light.value,
            pressure=pressure.value,
        ),
        "/music": v.radio(knob=enco.value),
    }

    m = rui.Menu(default="/summary", routes=routes)
    display = produce_display()
    display.root_group = m.group

    """Setup of polling coroutines"""

    async def sensor_polling_fn(
        sensors: list[s.SensorReader],
        sleep=0.1,  # s
    ):
        while True:
            with batch():
                for sensor, n in sensors:
                    sensor.update(n)
            await asyncio.sleep(sleep)

    loop = asyncio.get_event_loop()

    sensor_polling = loop.create_task(
        sensor_polling_fn(
            [
                (enco, 1),
                (light, 1),
            ],
            sleep=1 / 50,
        )
    )
    bme280_polling = loop.create_task(
        sensor_polling_fn(
            [
                (temperature, 1),
                (humidity, 1),
                (pressure, 1),
            ],
            sleep=1 / 20,
        )
    )

    # async def publish_data_fn(sleep):
    #     mqttc = produce_mqtt()
    #     while True:
    #         # with batch():
    #         mqttc.publish("telemetry/temperature", temperature.value())
    #             # async with Client(**mqttconn) as client:
    #             #     await client.publish("humidity/outside", payload=0.38)
    #         await asyncio.sleep(sleep)

    # publish_data_task = loop.create_task(publish_data_fn(
    #     mqttconn={
    #         "hostname": tb_mqtt_host,
    #         "client_id": "haptgp-f",
    #         "username": "haptgp-f",
    #         "password": "haptgp-f",
    #     },
    #     sleep=10
    # ))

    async def update_display_fn(refresh_period):
        while True:
            display.refresh()
            await asyncio.sleep(refresh_period)

    update_display_task = loop.create_task(update_display_fn(1 / 25))

    async def poll_touch():
        touch = cst816.CST816(i2c)
        while True:
            t = touch.get_touch()
            if t:
                if m.current.get() == "/summary":
                    m.current.set("/music")
                else:
                    m.current.set("/summary")
                print(f"changed route to {m.current.get()}")
            await asyncio.sleep(0.05)

    poll_touch_task = loop.create_task(poll_touch())

    try:
        tasks = asyncio.gather(
            sensor_polling,
            bme280_polling,
            update_display_task,
            poll_touch_task,
            # publish_data_task
        )
        loop.run_until_complete(tasks)
    except asyncio.CancelledError:
        pass
