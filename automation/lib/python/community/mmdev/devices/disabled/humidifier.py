from . import regulator
from . import sensor

from .. import device

class Humidifier(object):
    collection='Builtin'
    name='Humidifier'
    def __init__(self, rule_engine, room_name, device_name, **kwargs):
        dev = device.Device(
            device_class=Humidifier,
            room_name=room_name,
            device_name=device_name,
            rule_engine=rule_engine,
            **kwargs
        )

        self.__regulator = regulator.Regulator(
            device_class=Humidifier,
            room_name=room_name,
            device_name=device_name,
            cooldown_period=60.0,
            minimum_duty_period=60.0,
            window=0.05,
            rule_engine=rule_engine,
            **kwargs
        )

        self.__humidity = sensor.Sensor(
            device_class=Humidifier, 
            room_name=room_name, 
            device_name=device_name,
            property_name='Humidity',
            default=0.5,
            rule_engine=rule_engine,
            **kwargs
        )

        self.__setpoint = dev.property(
            'Setpoint', default=0.45
        )

        self.__away = device.State(
            'Away', 
            rule_engine=rule_engine,
            default=False
        )

    def __update(self):
        if self.__away.value:
            self.__regulator.setpoint = 0.3
        else:
            self.__regulator.setpoint = self.__setpoint.value   

    def __hysterisis(self, _, humidity):
        self.__regulator.hysterisis(humidity)

    def register(self):
        self.__regulator.register()
        self.__humidity.register()

        self.__setpoint.on_change()(self.__update)
        self.__away.on_change()(self.__update)
        self.__humidity.property.on_change(pass_context=True)(self.__hysterisis)

    @property
    def humidity(self):
        return self.__humidity.property

    @property
    def setpoint(self):
        return self.__setpoint

    @property
    def energized(self):
        return self.__regulator.energized
