import time


class PortableAC(object):
    collection='Builtin'
    name='PortableAC'

    def __init__(self, device, 
                 energized_channel=None, 
                 overheat=None):

        self.__last_transition = device.property(
            int, 'LastTransition', default=0.0
        )

        self.__energized = device.property(
            bool, 'Energized', default=False,
            channel=energized_channel
        )

        self.__overheat = overheat
        if self.__overheat:
            self.__overheat.on_change()(self.__update)
        device.rule_engine.loop()(self.__update)

    def __update(self):
        now = time.time()
        if self.__overheat and (self.__overheat.value != self.__energized.value) and (now - self.__last_transition.value > 30 * 60):
            self.__last_transition.value = now
            self.__energized.value = self.__overheat.value
        elif not self.__overheat and self.__energized.value and (now - self.__last_transition.value > 30 * 60):
            self.__last_transition.value = now
            self.__energized.value = False  


    @property
    def energized(self):
        return self.__energized
