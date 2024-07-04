
import time

from .. import device


class Lock(object):
    collection='Builtin'
    name='Lock'
    def __init__(self, rule_engine, **kwargs):
        dev = device.Device(
            device_class=Lock,
            rule_engine=rule_engine,
            **kwargs
        )

        self.__locked = dev.property(
            'Locked', default=False
        )

        self.__last_unlocked = 0.0
        self.__rule_engine = rule_engine

    def register(self):
        self.__locked.on_change(
            pass_context=True
        ) (
            self.__lock_change
        )
        
        self.__rule_engine.loop()(
            self.__update
        )

    def __lock_change(self, old, new):
        if old == True and new == False:
            self.__last_unlocked = time.time()

    def __update(self):
        if time.time() - self.__last_unlocked > 300.0:
            self.__locked.value = True

    @property
    def locked(self):
        return self.__locked
