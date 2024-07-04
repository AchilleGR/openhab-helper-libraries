from .. import device


class OccupancyDetector(object):
    collection='Builtin'
    name = 'OccupancyDetector'
    def __init__(self, **kwargs):
        dev = device.Device(device_class=OccupancyDetector, **kwargs)

        self.__presence = dev.property('Presence', default=True)

    @property
    def presence(self):
        return self.__presence
