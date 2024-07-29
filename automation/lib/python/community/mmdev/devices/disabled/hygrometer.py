from . import sensor


class Hygrometer(object):
    collection='Builtin'
    name = 'Hygrometer'
    def __init__(self, **kwargs):
        self.__sensor = sensor.Sensor(
            device_class=Hygrometer, 
            property_name='Humidity',
            **kwargs
        )

    def register(self):
        self.__sensor.register()
    
    @property
    def humidity(self):
        return self.__sensor.property
