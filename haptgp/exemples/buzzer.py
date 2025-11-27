"""testing status:
- [X] verified working
"""

import warnings
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
warnings.simplefilter("ignore")


# GPIO.PWM(board.D16)
buzzer = TonalBuzzer(16)
while True:
    buzzer.play(Tone("A4"))