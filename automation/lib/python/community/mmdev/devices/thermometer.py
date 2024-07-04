from . import sensor


class Thermometer(object):
    collection='Builtin'
    name = 'Thermometer'
    def __init__(self, **kwargs):
        self.__sensor = sensor.Sensor(
            device_class=Thermometer,
            property_name='Temperature',
            **kwargs
        )

    def register(self):
        self.__sensor.register()

    @property
    def temperature(self):
        return self.__sensor.property
