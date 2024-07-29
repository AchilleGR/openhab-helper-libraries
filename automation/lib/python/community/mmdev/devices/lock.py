import time


class Lock(object):
    collection='Builtin'
    name='Lock'

    def __init__(self, device, lock_channel=None):

        self.__locked = device.property(
            bool, 'Locked', default=True,
            metadata={'ga': ('Lock', {
                'lang': 'en',
                'roomHint': device.room_name,
                'name': device.device_name
            })},
            channel=lock_channel
        )

        self.__last_unlocked = device.property(
            int, 'LastUnlocked', default=0.0
        )

        self.__locked.on_change(
            pass_context=True
        ) (
            self.__lock_change
        )
        
        device.rule_engine.loop()(
            self.__update
        )

    def __lock_change(self, old, new):
        if old == True and new == False:
            self.__last_unlocked.value = time.time()

    def __update(self):
        if time.time() - self.__last_unlocked.value > 300.0:
            self.__locked.value = True

    @property
    def locked(self):
        return self.__locked
