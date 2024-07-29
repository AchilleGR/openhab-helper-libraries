import time


class Regulator(object):
    collection='Builtin'
    name='Regulator'
    def __init__(self,
                 device,
                 energized_channel,
                 cooldown_period=600.0, 
                 minimum_duty_period=600.0, 
                 window=0.05, 
                 default_setpoint=0.5, 
                 inverted=False):

        self.__energized = device.property(
            bool, 'RegulatorEnergized', 
            default=False, channel=energized_channel
        )

        self.__power = device.property(bool, 'RegulatorPower', default=False)

        self.__setpoint = 0.5

        self.__inverted = inverted
        self.__cooldown_period=cooldown_period
        self.__minimum_duty_period = minimum_duty_period
        self.__window = window
        self.__desired = False
        self.__rule_engine = device.rule_engine

        self.__last_transition = device.property(int, 'RegulatorLastTransition', default=time.time())

        self.__rule_engine.loop()(self.__update)
        self.__update()

    def __update(self):
        target = self.__desired and self.__power.value
        if self.__energized.value == target:
            return

        now = time.time()
        if target:
            if now - self.__last_transitionvalue >= self.__cooldown_period:
                self.__last_transition.value = now
                self.__energized.value = True
        else:
            if now - self.__last_transition.value >= self.__minimum_duty_period:
                self.__last_transition.value = now
                self.__energized.value = False
        
    def hysterisis(self, value):
        if self.__setpoint == 0.0:
            self.__desired = False
            self.__update()
            return

        if self.__inverted:
            if value < self.__setpoint:
                self.__desired = False
            elif value >= self.__setpoint  - self.__window:
                self.__desired = True
        else:
            if value > self.__setpoint:
                self.__desired = False
            elif value <= self.__setpoint  + self.__window:
                self.__desired = True

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
