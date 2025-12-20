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
import terminalio
from reaktiv import Computed, Effect
import vectorio
from typing import Callable
# from adafruit_display_text.bitmap_label import Label
from adafruit_display_text.label import Label

# from adafruit_display_text.

vectorio.Polygon

# TODO: replace "int" with actual types
Dispatch = int 
Store = int

View = Callable[[Store, Dispatch], displayio.Group]


# class SignalStore(dict[str, Signal]):
#     def take(self, *keys):
# TODO: return namespace instead
#         return [self[k] for k in keys]
        
def summary(enco, light, temperature, humidity, pressure,):
    root = displayio.Group(x=15, y=40)
    
    angle_round = Computed(lambda: round(enco() or 0.0, 1))
    
    def text_template(a, t, L, h, p):
        return f"""
        angle: {a or 0.0:>5.1f}°
        {t or 0.0:>8.2f}°C\t{L or 0.0:>8.0f}lux
        {h or 0.0:>8.2f}% \t{p or 0.0:>8.1f}kPa
        """
    
    text_lbl = Label(font=terminalio.FONT, text=text_template(0,0,0,0,0))
    root.append(text_lbl)
    
    @Effect
    def change_on_store_update():
        text_lbl.text = text_template(angle_round(), temperature(), light(), humidity(), pressure())
    
    return root

def radio(knob, music_service=0):
    root = displayio.Group(x=15, y=40)
    
    text_lbl = Label(font=terminalio.FONT, text="this shouldve played music")
    root.append(text_lbl)
    
    return root
