"""
custom input methods
"""


import time
import numpy as np
from reaktiv import Computed, LinkedSignal, Signal

from misc import MovingAnalysis, angular_dist


class KnobCtls:
    """
    Knob Controls

    step 1: make integral of encoder over x seconds (to be determined) (should not be average)
    step 2: detect direction of turn if average is larger than a threshold
        - direction is sign of integral
        - speed is strength of integral
    """

    def __init__(
        self,
        encoder: Signal[float],
        time_constant_s: float,
        stopped_variator: float,  # FIXME: degrees per second, shit name, basically how big the knob movement has to be for it to be considered moving.
    ):
        self.encoder = encoder
        self.last_pos = None
        self.__analisys = MovingAnalysis(x_cutoff=time_constant_s)
        self.__rotation = Computed(self.handle_rotation_update)
        self.speed = Computed(lambda: abs(self.__rotation()))
        self.direction = Computed(
            lambda: np.sign(self.__rotation())
            if self.speed() > stopped_variator
            else 0.0
        )
        
        
        def handle_dir_just_changed(new: float, previous):
            if previous is None:
                return {"actual": 0.0, "last_val": 0.0} # initialisation, basically
            if new == previous.value["last_val"]:
                return {"actual": 0.0, "last_val": previous.value["last_val"]}
            return {"actual": new, "last_val": new}
        
        self.direction_just_changed = LinkedSignal(
            source=self.direction,
            computation=handle_dir_just_changed,
        )

    def handle_rotation_update(self):
        curr_pos = self.encoder()
        if self.last_pos is None:
            self.last_pos = curr_pos
            return 0
        change = angular_dist(from_angle=self.last_pos, to_angle=curr_pos)
        self.__analisys.add(time.monotonic(), change)
        deg_per_sec = self.__analisys.derivative()
        self.last_pos = curr_pos
        return deg_per_sec
