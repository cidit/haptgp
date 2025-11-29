"""testing status:
- [X] verified working
"""

import warnings
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from time import sleep
warnings.simplefilter("ignore")

# https://gist.github.com/topshed/4e7ee1a5bbf5f35db2062029a9d4c390
v1 = ["G4", "G4", "G4", "D4", "E4", "E4", "D4"]
v2 = ["B4", "B4", "A4", "A4", "G4"]
v3 = ["D4", "G4", "G4", "G4", "D4", "E4", "E4", "D4"]

song = [v1,v2,v3,v2]

# GPIO.PWM(board.D16)
buzzer = TonalBuzzer(16)

for verse in song:
    for note in verse:
        buzzer.play(Tone(note))
        sleep(0.4)
        buzzer.stop()
        sleep(0.1)
    sleep(0.2)