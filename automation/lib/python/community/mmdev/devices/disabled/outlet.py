import time

from .. import device


class Outlet(object):
    collection='Builtin'
    name='Outlet'
    def __init__(self, **kwargs):

        self.device = device.Device(
            device_class=Outlet,
            **kwargs
        )

        self.__power = self.device.property(
            'Power', 
            default=True
        )

        self.__automatic_mode = self.device.property(
            'AutomaticMode', 
            default=True
        )

        self.__watts = self.device.property(
            'Watts', 
            default=0.0
        )

        self.__automatic_power = self.device.property(
            'AutomaticPower', 
            default=True
        )

        self.__energized = self.device.property(
            'Energized', 
            default=True
        )

    @property
    def energized(self):
        return self.__energized

    @property
    def power(self):
        return self.__power

    @property
    def automatic_mode(self):
        return self.__automatic_mode

    @property
    def automatic_power(self):
        return self.__automatic_power

    @property
    def watts(self):
        return self.__watts

    def register(self):
        self.__power.on_change()(self.__update)
        self.__automatic_power.on_change()(self.__update)
        self.__automatic_mode.on_change()(self.__update)

    def __update(self):
        if self.__automatic_mode.value:
            self.__energized.value = self.__automatic_power.value
        else:
            self.__energized.value = self.__power.value

