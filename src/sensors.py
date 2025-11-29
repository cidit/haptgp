from reaktiv import Signal
from smbus2 import SMBus
from adafruit_veml7700 import VEML7700
from typing import Callable
import pandas as p
from adafruit_bme280.advanced import Adafruit_BME280_I2C
import numpy as np



# Ce type de filtre ne fonctionne pas avec les angles (passage de 360 à 0 !!!!)
filtered_angle = 0
alpha = 0.1  # must be between 0 and 1 inclusive


class SensorReader:
    def __init__(self, aquire: Callable[[], float], calibration: p.DataFrame | None):
        self.value = Signal[float | None](None)
        self.aquire = aquire
        self.calibration = calibration
        # self.interpolation_function = interpolate.interp1d(
        #     x=calibration["reading"],
        #     y=calibration["reference"],
        #     assume_sorted=False,
        # ) if calibration is not None else None

    def read(self) -> float:
        reading = self.aquire()
        # if self.interpolation_function is None:
        #     return reading
        if self.calibration is None:
            return reading
        return np.interp(reading, xp=self.calibration["reading"], fp=self.calibration["reference"])
        # return self.interpolation_function(reading)

    def update(self):
        self.value.set(self.read())


class RotaryEncoder(SensorReader):
    
    # Define I2C bus number (e.g., 1 for Raspberry Pi 2/3/4)
    I2C_BUS_NUMBER = 1
    # Define the I2C address of your slave device (e.g., from i2cdetect)
    DEVICE_ADDRESS = 0x06  # Example: MT6701 address
    # Define the register address within the device to read/write
    REGISTER_DIR = 0x29  # DIR = 1 for CW (bit 1)
    REGISTER_ANGLE_MSB = 0x03  # Angle<13:6>
    REGISTER_ANGLE_LSB = 0x04  # Angle<5:0>

    ANGLE_MAX_DEGREES = 360.0
    ENCO_RESOLUTION_QUANTA = 1 / (2**14)
    
    def __init__(
        self, i2c_bus: int = I2C_BUS_NUMBER, device_address: int = DEVICE_ADDRESS, calibration = None
    ):
        super().__init__(aquire=self.aquire_fn, calibration=calibration)
        self.i2c_bus = i2c_bus
        self.device_address = device_address

    def aquire_fn(self):
        with SMBus(self.i2c_bus) as bus:
            # Read DIR REGISTER
            bytes1 = bus.read_byte_data(self.device_address, RotaryEncoder.REGISTER_DIR)
            # Set direction clockwise
            bytes1 = bytes1 | 0b00000010  # DIR = 1 for CW (bit 1)
            # Write DIR REGISTER
            bus.write_byte_data(self.device_address, RotaryEncoder.REGISTER_DIR, bytes1)
            # Read Angle MSB Register (Angle<13:6>) ... Bit7 to Bit0
            bytes1 = bus.read_byte_data(self.device_address, RotaryEncoder.REGISTER_ANGLE_MSB)
            # print(f"Read byte from register {hex(REGISTER_ADDRESS_MSB)}: {hex(bytes1)}")
            # Read Angle LSB Register (Angle<5:0>) ... Bit7 to Bit2
            bytes2 = bus.read_byte_data(self.device_address, RotaryEncoder.REGISTER_ANGLE_LSB)
            # print(f"Read byte from register {hex(REGISTER_ADDRESS_LSB)}: {hex(bytes2)}")
            # Concatenate bytes2 with bytes1
            angle_int = bytes2 >> 2
            angle_int = (bytes1 << 6) | angle_int
            new_angle = angle_int * RotaryEncoder.ANGLE_MAX_DEGREES * RotaryEncoder.ENCO_RESOLUTION_QUANTA
            return new_angle


class Light(SensorReader):
    def __init__(self, veml: VEML7700, calibration = None):
        super().__init__(aquire=self.aquire_fn, calibration=calibration)
        self.veml7700 = veml

    def aquire_fn(self):
        return self.veml7700.light

class Temperature(SensorReader):
    def __init__(self, bme: Adafruit_BME280_I2C, calibration = None):
        super().__init__(aquire=self.aquire_fn, calibration=calibration)
        self.bme = bme

    def aquire_fn(self):
        return self.bme.temperature
    

class Pressure(SensorReader):
    def __init__(self, bme: Adafruit_BME280_I2C, calibration = None):
        super().__init__(aquire=self.aquire_fn, calibration=calibration)
        self.bme = bme

    def aquire_fn(self):
        return self.bme.pressure
    

class Humidity(SensorReader):
    def __init__(self, bme: Adafruit_BME280_I2C, calibration = None):
        super().__init__(aquire=self.aquire_fn, calibration=calibration)
        self.bme = bme

    def aquire_fn(self):
        return self.bme.humidity
