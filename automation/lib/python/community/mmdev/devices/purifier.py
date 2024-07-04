from .. import device
from .. import log


class Purifier(object):
    collection='Builtin'
    name='Purifier'
    def __init__(self, rule_engine, logger, **kwargs):
        dev = device.Device(
            device_class=Purifier,
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__logger = logger

        self.__pm25 = dev.property(
            'PM25', default=0.0
        )

        self.__tvoc = dev.property(
            'TVOC', default=0.0
        )

        self.__automatic_mode = dev.property(
            'AutomaticMode', default=True
        )

        self.__automatic_fan_speed = dev.property(
            'AutomaticFanSpeed', default=0.0
        )

        self.__manual_fan_speed = dev.property(
            'ManualFanSpeed', default=0.0
        )

        self.__real_fan_speed = dev.property(
            'RealFanSpeed', default=0.0
        )

        self.__sleeping = device.State(
            'Sleeping', 
            rule_engine=rule_engine,
            default=False
        )

        self.__automatic_air_regulation = device.State(
            'AutomaticAirRegulation', 
            rule_engine=rule_engine,
            default=False
        )

    @property
    def pm25(self):
        return self.__pm25

    @property
    def tvoc(self):
        return self.__tvoc

    def register(self):
        self.__tvoc.on_change()(self.__update)
        self.__pm25.on_change()(self.__update)
        self.__automatic_air_regulation.on_command(
            pass_context=True
        ) (
            self.__auto_mode_update
        )
        self.__automatic_mode.on_change()(self.__update)
        self.__sleeping.on_change()(self.__update)
        self.__manual_fan_speed.on_change()(self.__manual_update)

    @property
    def automatic_mode(self):
        return self.__automatic_mode

    @property
    def automatic_fan_speed(self):
        return self.__automatic_fan_speed

    @property
    def manual_fan_speed(self):
        return self.__manual_fan_speed

    @property
    def real_fan_speed(self):
        return self.__real_fan_speed

    def __auto_mode_update(self, new):
        self.__logger.error('TRACE: Air Regulation Called: %s' % new)
        if new:
            self.__manual_fan_speed.update(0)
            self.__automatic_mode.value = True
            self.__update()

    def __manual_update(self):
        self.__automatic_mode.value = False
        self.__update()

    def __update(self):

        air_quality_perc = 1.0 - max(0.0, min(1.0, (self.__pm25.value - 5.0) / 20.0))
        tvoc_ppm_perc = 1.0 - max(0.0, min(1.0, self.__tvoc.value / 12000.0))

        fan_speed = 1.0 - min(tvoc_ppm_perc, air_quality_perc)
        self.__automatic_fan_speed.value = fan_speed

        if not self.__automatic_mode.value:
            self.__real_fan_speed.value = self.__manual_fan_speed.value
        elif self.__sleeping.value:
            self.__real_fan_speed.value = min(0.33, fan_speed)
        else:
            self.__real_fan_speed.value = fan_speed
