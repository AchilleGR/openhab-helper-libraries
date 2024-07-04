from . import regulator
from . import sensor
from . import thermostat

from .. import device
from .. import manager


class Dehumidifier(object):
    collection='Builtin'
    name='Dehumidifier'

    def __init__(self, rule_engine, room_name, device_name, logger, **kwargs):
        self.__manager = manager.Manager(
            logger=logger, rule_engine=rule_engine
        )

        self.device = device.Device(
            device_class=Dehumidifier,
            room_name=room_name,
            device_name=device_name,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__regulator = regulator.Regulator(
            device_class=Dehumidifier, 
            room_name=room_name,
            device_name=device_name, 
            inverted=True, 
            cooldown_period=600.0,
            minimum_duty_period=300.0,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__humidity = sensor.Sensor(
            device_class=Dehumidifier, 
            room_name=room_name, 
            device_name=device_name,
            property_name='Humidity',
            default=0.6,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__weather_humidity = sensor.Sensor(
            device_class=Dehumidifier, 
            room_name=room_name, 
            device_name=device_name,
            property_name='WeatherHumidity',
            default=0.6,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__setpoint = self.device.property(
            'Setpoint', default=0.60
        )

        self.__away = device.State(
            'Away', 
            rule_engine=rule_engine,
            default=False
        )

    @property 
    def overheat(self):
        return self.__overheat

    @property
    def thermostat(self):
        for _, stat in self.__manager.devices_for(device_class=thermostat.Thermostat, room_name=self.device.room_name):
            return stat
        for _, stat in self.__manager.devices_for(device_class=thermostat.Thermostat):
            return stat

    def __update(self):
        if self.__setpoint.value == 1.0:
            self.__setpoint.value = 0.5

        overheat = False
        if self.thermostat is not None:
            _, high, mode = self.thermostat.operation()
            temp = self.thermostat.temperature.value
            overheat = 'Cool' in mode and temp > high

        if self.__away.value or overheat:
            setpoint = 1.0
        else:
            setpoint = self.__setpoint.value   

        if setpoint < self.__weather_humidity.property.value:
            setpoint = self.__weather_humidity.property.value

        if self.__setpoint.value == 0.0:
            self.__regulator.power.value = False
        else:
            self.__regulator.setpoint = min(max(0.3, setpoint), 0.7)
            self.__regulator.power.value = True


    def __hysterisis(self, _, humidity):
        self.__regulator.hysterisis(humidity)

    def register(self):
        self.__regulator.register()
        self.__humidity.register()
        self.__weather_humidity.register()

        self.__setpoint.on_change()(self.__update)
        self.__weather_humidity.property.on_change()(self.__update)
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
