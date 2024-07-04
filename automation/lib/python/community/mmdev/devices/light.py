from .. import device


class Light(object):
    collection='Builtin'
    name='Light'
    def __init__(self, rule_engine, room_name, logger, **kwargs):
        dev = device.Device(
            rule_engine=rule_engine,
            room_name=room_name,
            device_class=Light,
            logger=logger,
            **kwargs
        )

        self.__real_color = dev.property(
            'RealColor', default=(1.0, 1.0, 1.0)
        )

        self.__power = dev.property(
            'Power', default=False
        )

        self.__state_color = dev.property(
            'StateColor', default=(1.0, 1.0, 1.0)
        )

        self.__manual_color = dev.property(
            'ManualColor', default=(1.0, 1.0, 1.0)
        )

        self.__motion_detection = dev.property(
            'MotionDetection', default=False
        )

        self.__automatic_color_temperature = dev.property(
            'AutomaticColorTemperature', default=6500.0
        )

        self.__automatic_mode = dev.property(
            'AutomaticMode', default=True
        )

        self.__real_color_temperature = dev.property(
            'RealColorTemperature', force=True
        )

        self.__real_color_temperature_abs = dev.property(
            'RealColorTemperatureAbs', force=True
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

        self.__room_name = room_name
        self.__automatic_mode.value = True
        self.__logger = logger
        self.__off_trigger = False

    @property
    def manual_color(self):
        return self.__manual_color

    @property
    def automatic_color_temperature(self):
        return self.__automatic_color_temperature

    @property
    def motion_detection(self):
        return self.__motion_detection

    @property
    def power(self):
        return self.__power

    @property
    def automatic_mode(self):
        return self.__automatic_mode

    def __dog_away_change(self, _, dog_away):
        if dog_away:
            if self.__away.value:
                self.__color_command(False)

    def __away_change(self, _, away):
        if away:
            if self.__dog_away.value:
                self.__color_command(False)
            else:
                if self.__room_name == 'Bedroom':
                    self.__color_command(0.33)
                    self.__color_command(True)
                else:
                    self.__color_command(False)
                    self.__color_command(1.0)
        else:
            self.__color_command(1.0)
            if self.__room_name == 'Bedroom':
                self.__color_command(True)

    def __sleeping_change(self, _, sleeping):
        if sleeping:
            if self.__room_name == 'Bathroom':
                self.__color_command(0.6)
                self.__color_command(True)
            else:
                self.__color_command(0.15)
                if self.__room_name in ['Hallway', 'LivingRoom']:
                    self.__color_command(True)
                else:
                    self.__color_command(False)
        else:
            self.__color_command(1.0)
            if self.__room_name != 'Closet':
                self.__color_command(True)

    def register(self):
        self.__state_color.on_change()(self.__update)
        self.__power.on_change()(self.__update)
        self.__motion_detection.on_change()(self.__update)
        self.__automatic_color_temperature.on_change()(self.__update)
        self.__automatic_mode.on_change()(self.__update)

        self.__manual_color.on_command(
            pass_context=True
        ) (
            self.__color_command
        )

        self.__away.on_change(pass_context=True)(self.__away_change)
        self.__sleeping.on_change(pass_context=True)(self.__sleeping_change)
        self.__dog_away.on_change(pass_context=True)(self.__dog_away_change)

    def __color_command(self, command):
        if isinstance(command, tuple) or isinstance(command, list):
            new_h, new_s, _ = command
            _, _, old_b = self.__state_color.value
            if old_b <= 0.05:
                self.__state_color.command((new_h, new_s, 0.05), force=True)
            else:
                self.__state_color.command((new_h, new_s, old_b), force=True)
            if self.__sleeping.value:
                self.__power.command(True, force=True)
            else:
                self.__automatic_mode.command(True, force=True)

        elif isinstance(command, float):
            old_h, old_s, _ = self.__state_color.value
            if command <= 0.05:
                self.__state_color.command((old_h, old_s, 0.05), force=True)
            else:
                self.__state_color.command((old_h, old_s, command), force=True)
            if self.__sleeping.value:
                self.__power.command(True, force=True)

        elif isinstance(command, bool):
            if not command:
                self.__off_trigger = True
            self.__power.command(command, force=True)

    def __update(self):
        motion_detection = self.__motion_detection.value
        if not motion_detection:
            self.__off_trigger = False

        power = ((not self.__off_trigger) and motion_detection) or self.__power.value
        self.__real_color.value = power
        if power:
            if self.__automatic_mode.value:

                temp = self.automatic_color_temperature.value
                if self.__real_color_temperature_abs.exists:
                    if temp < 1201.0:
                        temp = 1201.0
                    elif temp > 6500.0:
                        temp = 6500.0
                    self.__real_color_temperature_abs.value = temp
                    
                else:
                    if temp < 2000.0:
                        perc = 1.0
                    elif temp > 6500.0:
                        perc = 0.01
                    else:
                        perc = 1.0 - ((temp - 2000.0) / (6500.0 - 2000.0))
                    self.__real_color_temperature.value = perc

                self.__real_color.value = self.__state_color.value[2]
            else:
                self.__real_color.value = self.__state_color.value
