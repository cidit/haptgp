from logging import warning
import displayio
from reaktiv import Signal, Effect


class Menu():
    def __init__(self, routes: dict[str, displayio.Group], default: str | None):
        assert len(routes) > 0
        self.group = displayio.Group()
        self.routes = routes
        for group in routes.values():
            self.group.append(group)
        self.current = Signal(default or routes.keys()[0])
        if self.current() not in routes.keys():
            raise ValueError(f"default route {default} is not valid for {routes.keys()}")
        self.hide_all()
        self.__the_effect_ref = Effect(self.__the_effect_fn)
        
    def __the_effect_fn(self):
        if self.current() not in self.routes.keys():
            warning(f"default route {self.current()} is not valid for {self.routes.keys()}")
            return
        self.hide_all()
        self.routes[self.current()].hidden = False
            
    def hide_all(self):
        for widget in self.routes.values():
            widget.hidden = True