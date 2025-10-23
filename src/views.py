"""view hierarchy

main menu
- [view] weather station
    - displays the following datapoint buttons
        - light level
        - temp
        - humidity
        - pressure
    - [controls]
        - turn counterclock to go back
        - touch a button to enter focus
    - [view] focus
        - focused view of the datapoints
        - [controls]
            - click once to show controls
            - turn clockwise to enter calibration (?)
            - turn counterclock to go back
            - click again to hide controls
- [view] play song
    - plays currently selected song automatically
    - [controls]
        - click once to show controls
        - turn clockwise to enter song selection
        - turn counterclock to go back
        - click again to hide controls
    - [view] song selection
        - [controls]
            - turn clockwise to scroll down
            - turn counterclock to scroll up
            - click on a song to select it and go back
- [view] show time
    - shows time
    - [controls]
        - click once to show controls
        - turn clockwise to enter calibration (?)
        - turn counterclock to go back
        - click again to hide controls
- [view] info
    - shows the following info:
        - endpoint for config panel
        - currently connected network name
        - hostname and/or local ip

"""

import displayio
from vectorio import Circle
from typing import Callable
# from adafruit_display_text.


# TODO: replace "int" with actual types
Dispatch = int 
Store = int
View = Callable[[Store, Dispatch], displayio.Group]


def main_menu_view(palette: displayio.Palette):
    root = displayio.Group()
    return root

def single_datapoint_view( label: str, value: float, unit: str):
    """
    - shows one datapoint in big.
    - click anywhere to show controls
        - click anywhere to hide controls
        - turn right to enter calibration mode (?) # TODO
        - turn left to go back to weather_station_view
    """
    pass

def light_level_view():
    return single_datapoint_view("Light Level", 0.0, "lux")

def temperature_view():
    return single_datapoint_view("Temperature", 0.0, "°C")

def humidity_view():
    return single_datapoint_view("Humidity", 0.0, "%")

def pressure_view():
    return single_datapoint_view("Pressure", 0.0, "kPa")

def weather_station_view():
    """
    displays 4 quarter circles with each measurements in real time.
    measurements can be clicked to go to the full screen view of that measurement
    """
    pass