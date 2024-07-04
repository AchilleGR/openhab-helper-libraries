import math

from .. import device
from . import sensor
from . import dehumidifier
from .. import utils
from .. import manager
        

_DEFAULT_THERMOSTAT_MODES={
    'Off': 0, 
    'Heat': 1, 
    'Cool': 2, 
    'HeatCool': 3,
    'AwayHeat': 11,
    'AwayCool': 12
}


_DEFAULT_THERMOSTAT_FAN_MODES={
    'Auto': 0,
    'On': 1,
    'Circulate': 6
}


class Thermostat(object):
    collection='Builtin'
    name = 'Thermostat'
    def __init__(self, 
                 rule_engine,
                 logger,
                 **kwargs):

        self.__manager = manager.Manager(
            rule_engine=rule_engine,
            logger=logger
        )

        self.device = device.Device(
            device_class=Thermostat, 
            rule_engine=rule_engine,
            logger=logger,
            **kwargs
        )

        self.__logger = logger
        self.__rule_engine = rule_engine

        self.__temperature = sensor.Sensor(
            device_class=Thermostat,
            rule_engine=rule_engine,
            property_name='Temperature',
            logger=logger,
            **kwargs
        )

        self.__humidity = sensor.Sensor(
            device_class=Thermostat,
            rule_engine=rule_engine,
            property_name='Humidity',
            logger=logger,
            normalize=True,
            **kwargs
        )

        self.__modes = _DEFAULT_THERMOSTAT_MODES
        self.__fan_modes = _DEFAULT_THERMOSTAT_FAN_MODES

        self.__mode = self.device.property(
            'Mode', default=3.0
        )

        self.__fan_mode = self.device.property(
            'FanMode', default=0.0
        )

        self.__setpoint_low = self.device.property(
            'SetpointLow', default=68.0
        )

        self.__setpoint_high = self.device.property(
            'SetpointHigh', default=72.0
        )

        self.__real_setpoint_low = self.device.property(
            'RealSetpointLow', default=68.0
        )

        self.__real_setpoint_high = self.device.property(
            'RealSetpointHigh', default=72.0
        )

        self.__setpoint = self.device.property(
            'Setpoint', default=70.0
        )

        self.__real_setpoint = self.device.property(
            'RealSetpoint', default=70.0
        )
        
        self.__real_mode = self.device.property(
            'RealMode', default=3.0
        )

        self.__sleeping = device.State(
            'Sleeping', 
            rule_engine=rule_engine,
            default=False
        )

        self.__away = device.State(
            'Away', 
            rule_engine=rule_engine,
            default=False
        )

        self.__dog_away = device.State(
            'DogAway', 
            rule_engine=rule_engine,
            default=False
        )

    def __mode_translate(self, mode_num, mode_defs):
        for mode, num in mode_defs.items():
            if num == mode_num:
                return mode

    def __mode_set(self, mode_property, value, mode_defs):
        mode_property.value = float(int(mode_defs[value]))

    @property
    def mode(self):
        return self.__mode_translate(self.__mode.value, self.__modes)

    @mode.setter
    def mode(self, value):
        self.__mode_set(self.__mode, value, self.__modes)
        
    @property
    def fan_mode(self):
        return self.__mode_translate(self.__fan_mode.value, self.__fan_modes)

    @fan_mode.setter
    def fan_mode(self, value):
        self.__mode_set(self.__fan_mode, value, self.__fan_modes)

    @property
    def setpoint(self):
        return (
            self.__setpoint_low.value,
            self.__setpoint_high.value
        )

    @setpoint.setter
    def setpoint(self, values):
        try:
            low, high = values
            if low is not None:
                self.__setpoint_low.value = low
            if high is not None:
                self.__setpoint_high.value = high
        except:
            if values is not None:
                self.__setpoint = values

    @property
    def temperature(self):
        return self.__temperature.property

    @property
    def humidity(self):
        return self.__humidity.property

    @property
    def cooling(self):
        return self.mode in ('Cool', 'HeatCool')

    @property
    def heating(self):
        return self.mode in ('Heat', 'HeatCool')

    def register(self):
        self.__temperature.register()
        self.__humidity.register()

        self.__rule_engine.loop()(self.__update)

        self.__mode.on_change(
            pass_context=True
        ) (
            self.__update_mode
        )

    def __update_mode(self, old_mode, new_mode):
        old_mode = self.__mode_translate(old_mode, self.__modes)
        new_mode = self.__mode_translate(new_mode, self.__modes)

        if new_mode == 'Off':
            return

        elif old_mode in ('Heat', 'Cool') and new_mode in ('Heat', 'Cool'):
            return

        elif old_mode in ('Heat', 'Cool') and new_mode == 'HeatCool':
            setpoint = self.__setpoint.value
            self.__setpoint_low.value = setpoint
            self.__setpoint_high.value = setpoint

        elif new_mode in ('Heat', 'Cool') and old_mode == 'HeatCool':
            self.__setpoint.value = (float(self.__setpoint_low.value) + float(self.__setpoint_high.value)) / 2.0

        elif old_mode == 'Off' and new_mode in ('Heat', 'Cool'):
            self.__setpoint.value = 72.0

        elif old_mode == 'Off' and new_mode == 'HeatCool':
            self.__setpoint_low.value = 72.0
            self.__setpoint_high.value = 72.0

    def operation(self, temperature=None):
        low, high = self.setpoint
        if temperature is None:
            temperature = self.__temperature.property.value
        mode = self.mode

        if self.__away.value:
            if mode in ('AwayHeat', 'AwayCool'):
                if temperature >= 74.0:
                    return low, high, 'AwayCool'
                elif temperature <= 61.0:
                    return low, high, 'AwayHeat'
            else:
                if temperature >= 70.0:
                    return low, high, 'AwayCool'
                else:
                    return low, high, 'AwayHeat'

        if self.__sleeping.value:
            return 65, 65, 'HeatCool'
        
        return int(low), int(high), mode


    def __update(self):
        low, high = self.setpoint
        temperature = self.__temperature.property.value
        mode = self.mode

        target_low, target_high, target_mode = self.operation(temperature)
        target_setpoint = self.__setpoint.value

        if target_mode in ('Heat', 'Cool'):
            self.__real_mode.value = self.__modes[target_mode]
            if target_mode == 'Heat':
                self.__real_setpoint_low.value = target_setpoint
            elif target_mode == 'Cool':
                self.__real_setpoint_high.value = target_setpoint

        elif target_mode == 'Off':
            self.__real_mode.value = self.__modes['Off']
        elif target_mode == 'HeatCool':
            #if temperature >= target_high + 2.0:
            #    self.__real_mode.value = self.__modes['Cool']
            #    self.__real_setpoint_high.value = target_high
            #elif temperature <= target_low - 2.0:
            #    self.__real_mode.value = self.__modes['Heat']
            #    self.__real_setpoint_low.value = target_low
            #else: 
            self.__real_mode.value = self.__modes['HeatCool']
            self.__real_setpoint_low.value = target_low
            if target_low >= target_high:
                self.__real_setpoint_high.value = target_low
                self.__real_setpoint_low.value = target_low
            else:
                self.__real_setpoint_high.value = target_high
                self.__real_setpoint_low.value = target_low

        fan_mode = 'Auto' if 'Heat' in self.mode else 'Circulate'
        for _, dehumid in self.__manager.devices_for(device_class=dehumidifier.Dehumidifier):
            if dehumid.energized.value:
                fan_mode = 'On'

        self.__fan_mode = fan_mode
