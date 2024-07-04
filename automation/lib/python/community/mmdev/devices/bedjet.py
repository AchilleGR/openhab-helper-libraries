import math

from .. import device
from . import sensor
from .. import utils
        

_BEDJET_MODES=sorted([
    "HEAT",
    "DRY",
    "FAN_ONLY",
    "OFF"
])


class BedJet(object):
    collection='Builtin'
    name = 'BedJet'
    def __init__(self, 
                 rule_engine,
                 logger,
                 **kwargs):

        dev = device.Device(
            device_class=BedJet,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__logger = logger
        self.__rule_engine = rule_engine

        self.__temperature = sensor.Sensor(
            device_class=BedJet,
            rule_engine=rule_engine,
            property_name='Temperature',
            logger=logger,
            transform=lambda temp: (temp * 9.0 / 5.0) + 32.0,
            **kwargs
        )

        self.__real_mode = dev.property(
            'RealMode', default='OFF'
        )

        self.__mode = dev.property(
            'Mode', default='OFF'
        )

        self.__real_setpoint = dev.property(
            'RealSetpoint', default=70.0 * 9.0 / 5.0 + 32.0
        )

        self.__setpoint = dev.property(
            'Setpoint', default=70.0
        )

        self.__real_fan_speed = dev.property(
            'RealFanSpeed', default=0.2
        )

        self.__fan_speed = dev.property(
            'FanSpeed', default=1.0
        )
        
    def register(self):
        self.__temperature.register()

        self.__fan_speed.on_change()(self.__update_fan_speed)
        self.__mode.on_change()(self.__update_fan_speed)

    def __update_fan_speed(self):

        if self.__mode.value != 'AUTO':
            self.__real_fan_speed = self.__fan_speed * 0.2
            return

        self.__real_fan_speed = 0.2
