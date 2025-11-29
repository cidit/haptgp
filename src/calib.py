import board
import adafruit_veml7700
import pandas as p
import os
import time


CALIBRATION_DIR = "calibrations"


def get_latest_calibration(calib_type):
    current_latest_timestamp = 0
    current_latest = None
    for entry in os.scandir(CALIBRATION_DIR):
        if entry.is_file():
            (
                type,
                timestamp,
                *_
            ) = entry.name.split(".")
            timestamp = int(timestamp)
            if type == calib_type and timestamp > current_latest_timestamp:
                current_latest = f"{CALIBRATION_DIR}/{entry.name}"
                current_latest_timestamp = timestamp
    if current_latest is None:
        raise ValueError(
            f"No calibration in ./{CALIBRATION_DIR} that matches type {calib_type}"
        )
    return p.read_csv(current_latest)


def get_calibration(type, override=None):
    if override:
        return p.read_csv(override)
    get_latest_calibration(type)


def calibrate_light():
    datapoints = p.DataFrame({"reference": [], "reading": []})
    i2c = board.I2C()  # uses board.SCL and board.SDA
    veml7700 = adafruit_veml7700.VEML7700(i2c)

    while True:
        try:
            reference = float(
                input(
                    "what is the reference device showing now? (-1 to stop calibration)"
                )
            )
        except ValueError:
            print("couldnt parse. try again.")
            continue
        if reference == -1.0:
            print("ending calibration.")
            break
        reading = veml7700.light
        print("current value read:", reading)
        datapoints.loc[len(datapoints)] = [reference, reading]

    filepath = f"{CALIBRATION_DIR}/light.{int(time.time())}.csv"
    print("[!] saved at:", filepath)
    print(datapoints)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    datapoints.to_csv(filepath, index=False)
