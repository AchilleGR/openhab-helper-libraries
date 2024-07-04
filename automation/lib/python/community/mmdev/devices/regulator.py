import time

from .. import device


class Regulator(object):
    collection='Builtin'
    name='Regulator'
    def __init__(self,
                 rule_engine,
                 cooldown_period=600.0, 
                 minimum_duty_period=600.0, 
                 window=0.05, 
                 default_setpoint=0.5, 
                 inverted=False, 
                 **kwargs):

        self.__device = device.Device(
            rule_engine=rule_engine,
            **kwargs
        )

        self.__energized = self.__device.property(
            'Energized', 
            default=True
        )

        self.__power = self.__device.property(
            'Power', 
            default=True
        )

        self.__setpoint = 0.5

        self.__inverted = inverted
        self.__last_transition = time.time()
        self.__cooldown_period=cooldown_period
        self.__minimum_duty_period = minimum_duty_period
        self.__window = window
        self.__desired = False
        self.__rule_engine = rule_engine

    def register(self):
        self.__rule_engine.loop()(self.__update)

    def __update(self):
        target = self.__desired and self.__power.value
        if self.__energized.value == target:
            return

        now = time.time()
        if target:
            if now - self.__last_transition >= self.__cooldown_period:
                self.__last_transition = now
                self.__energized.value = True
        else:
            if now - self.__last_transition >= self.__minimum_duty_period:
                self.__last_transition = now
                self.__energized.value = False


    def hysterisis(self, value):
        if self.__setpoint == 0.0:
            self.__desired = False
            return

        if not self.__inverted:
            on = True
            off = False
            top = self.__setpoint
            bottom = self.__setpoint - self.__window
        else:
            on = False
            off = True
            top = self.__setpoint + self.__window
            bottom = self.__setpoint

        if value > top:
            self.__desired = off

        elif value < bottom:
            self.__desired = on
        self.__update()

    @property
    def energized(self):
        return self.__energized

    @property
    def power(self):
        return self.__energized

    @property
    def setpoint(self):
        return self.__setpoint

    @setpoint.setter
    def setpoint(self, value):
        self.__setpoint = value

    @property
    def device(self):
        return self.__device
