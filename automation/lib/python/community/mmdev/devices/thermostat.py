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

    def __init__(self, device, 
                 sleeping=None, 
                 away=None, 
                 temperature_channel=None, 
                 humidity_channel=None, 
                 dehumidifier_energized=None, 
                 fan_mode_channel=None, 
                 setpoint_low_channel=None, 
                 setpoint_high_channel=None, 
                 portableac_energized=None, 
                 mode_channel=None,
                 auto_mode=None,
                 overheat=None,
                 overcool=None):

        self.__overheat = overheat
        self.__overcool = overcool
        self.__logger = device.logger
        self.__rule_engine = device.rule_engine

        self.__group = device.group(
            'Thermostat_' + device.room_name.replace(' ', '') + '_' + device.device_name.replace(' ', ''),
            metadata={'ga': ('Thermostat', {
                'name': device.device_name,
                'roomHint': device.room_name,
                'lang': 'en',
                'useFahrenheit': True,
                'thermostatModes': 'off=0,heat=1,cool=2,heatcool=3'
            })}
        )

        self.__temperature = device.property(
            int, 'Temperature', default=0,
            channel=temperature_channel,
            groups=[self.__group.item],
            metadata={'ga': ('thermostatTemperatureAmbient', {})}
        )

        self.__humidity = device.property(
            float, 'Humidity', default=0,
            channel=humidity_channel,
            groups=[self.__group.item],
            normalize=True,
            metadata={'ga': ('thermostatHumidityAmbient', {})}
        )

        self.__modes = _DEFAULT_THERMOSTAT_MODES
        self.__fan_modes = _DEFAULT_THERMOSTAT_FAN_MODES

        self.__mode = device.property(
            int, 'Mode', default=3,
            groups=[self.__group.item],
            metadata={'ga': ('thermostatMode', {})}
        )

        self.__fan_mode = device.property(
            int, 'FanMode', default=6,
            channel=fan_mode_channel
        )

        self.__setpoint_low = device.property(
            int, 'SetpointLow', default=68.0,
            groups=[self.__group.item],
            metadata={'ga': ('thermostatTemperatureSetpointLow', {})}
        )

        self.__setpoint_high = device.property(
            int, 'SetpointHigh', default=72.0,
            groups=[self.__group.item],
            metadata={'ga': ('thermostatTemperatureSetpointHigh', {})}
        )

        self.__real_setpoint_low = device.property(
            int, 'RealSetpointLow', default=68.0,
            channel=setpoint_low_channel
        )

        self.__real_setpoint_high = device.property(
            int, 'RealSetpointHigh', default=72.0,
            channel=setpoint_high_channel
        )

        self.__setpoint = device.property(
            int, 'Setpoint', default=70.0,
            groups=[self.__group.item],
            metadata={'ga': ('thermostatTemperatureSetpoint', {})}
        )

        self.__real_mode = device.property(
            int, 'RealMode', default=3,
            channel=mode_channel
        )

        self.__sleeping = sleeping
        self.__away = away
        self.__dehumidifier_energized = dehumidifier_energized
        self.__portableac_energized = portableac_energized
        self.__auto_mode = auto_mode

        device.rule_engine.loop()(self.__update)

        self.__mode.on_change(
            pass_context=True
        ) (
            self.__update_mode
        )

        if self.__auto_mode:
            self.__auto_mode.on_change()(self.__update)
        if self.__dehumidifier_energized:
            self.__dehumidifier_energized.on_change()(self.__update)
        if self.__portableac_energized:
            self.__portableac_energized.on_change()(self.__update)

        self.__update()

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
    def mode_id(self):
        return self.__mode
        
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

    def on_mode_change(*args, **kwargs):
        self, args = args[0], args[1:]
        return self.__mode.on_change(*args, **kwargs)

    def on_operation_change(self, func):
        self.__setpoint.on_change()(func)
        self.__setpoint_low.on_change()(func)
        self.__setpoint_high.on_change()(func)
        self.__mode.on_change()(func)
        return func

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
        mode = self.mode
        if self.__auto_mode and self.__auto_mode.value:
            if self.__sleeping and self.__sleeping.value:
                return 65, 65, 65, 'HeatCool'
            else:
                return 70, 68, 72, 'HeatCool'
        return int((low + high) / 2), int(low), int(high), mode

    def __update(self):
        temperature = self.__temperature.value #* (9.0 / 5.0) + 32.0
        target_setpoint, target_low, target_high, target_mode = self.operation(temperature)

        if target_mode in ('Heat', 'Cool'):
            self.__real_mode.value = self.__modes[target_mode]
            if target_mode == 'Heat':
                self.__real_setpoint_low.value = target_setpoint
            elif target_mode == 'Cool':
                self.__real_setpoint_high.value = target_setpoint

        elif target_mode == 'Off':
            self.__real_mode.value = self.__modes['Off']
        elif target_mode == 'HeatCool':
            if temperature >= target_high + 2.0:
                self.__real_mode.value = self.__modes['Cool']
                self.__real_setpoint_high.value = target_high
            elif temperature <= target_low - 2.0:
                self.__real_mode.value = self.__modes['Heat']
                self.__real_setpoint_low.value = target_low
            else: 
                self.__real_mode.value = self.__modes['HeatCool']
                self.__real_setpoint_low.value = target_low
                if target_low >= target_high:
                    self.__real_setpoint_high.value = target_low
                else:
                    self.__real_setpoint_high.value = target_high

        fan_mode = 'Circulate'
        if self.__dehumidifier_energized and self.__dehumidifier_energized.value:
            fan_mode = 'On'
        if self.__portableac_energized and self.__portableac_energized.value:
            fan_mode = 'On'

        self.__fan_mode = fan_mode

        if self.__overheat:
            self.__overheat.value = 'Cool' in target_mode and temperature > target_high
        if self.__overcool:
            self.__overcool.value = 'Heat' in target_mode and temperature < target_low

        if self.__auto_mode and self.__auto_mode.value:
            self.__setpoint_low.update = self.__real_setpoint_low.value
            self.__setpoint_high.update = self.__real_setpoint_high.value
            if target_mode == 'Heat':
                self.__setpoint.update = self.__real_setpoint_low.value
            if target_mode == 'Cool':
                self.__setpoint.update = self.__real_setpoint_high.value
            self.__mode.update = self.__real_mode.value
