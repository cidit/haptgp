
def angular_dist(from_angle, to_angle):
    PI_DEG = 180
    zeroed = to_angle - from_angle
    if zeroed > PI_DEG:
        return zeroed - 2 * PI_DEG
    if zeroed < -PI_DEG:
        return zeroed + 2 * PI_DEG
    return zeroed


class MovingAnalysis:
    def __init__(self, x_cutoff):
        self.x = []
        self.y = []
        self.x_cutoff = x_cutoff  # this is basically the size of the window

    def add(self, x, y):
        self.x.append(x)
        self.y.append(y)

    def integral(self):
        self.__prune()  # shoot first, ask questions later. more seriously, avoids memory overflow.
        if len(self.x) == 0:
            return 0.0
        return sum(self.y)

    def average(self):
        # TODO: not used, but simple to just implement, why not
        return self.integral() / len(self.x)

    def derivative(self):
        deltax = self.x[-1] - self.x[0]
        return self.integral() / deltax

    def __prune(self):
        """
        gets rid of the values outside the window we are examining.
        """
        if len(self.x) == 0:
            return
        last_x = self.x[-1]
        idx_to_prune = [
            idx for idx, x in enumerate(self.x) if x < last_x - self.x_cutoff
        ]
        for prune in reversed(idx_to_prune):
            self.x.pop(prune)
            self.y.pop(prune)
