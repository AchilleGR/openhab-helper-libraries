from . import regulator


class Dehumidifier(object):
    collection='Builtin'
    name='Dehumidifier'

    def __init__(self, device, 
                 energized_channel=None, 
                 humidity_channel=None, 
                 weather_humidity_channel=None,
                 auto_mode=None,
                 sleeping=None,
                 overheat=None,
                 away=None, dog_away=None):

        self.__regulator = regulator.Regulator(
            device=device,
            inverted=True, 
            cooldown_period=300.0,
            minimum_duty_period=300.0,
            energized_channel=energized_channel
        )

        self.__humidity = device.property(
            float, 'Humidity',
            default=0.6,
            channel=humidity_channel
        )

        self.__weather_humidity = device.property(
            float, 'WeatherHumidity',
            default=0.6, 
            channel=weather_humidity_channel
        )

        self.__setpoint = device.property(
            float, 'Setpoint', 
            default=0.60,
            metadata={
                'ga': ('Fan', {
                    'lang': 'en',
                    'roomHint': device.room_name,
                    'name': device.device_name
                })
            }
        )

        self.__auto_mode = auto_mode
        self.__sleeping = sleeping
        self.__overheat = overheat
        
        if self.__auto_mode is not None:
            self.__auto_mode.on_change()(self.__update)
        self.__setpoint.on_command()(self.__command_setpoint)
        self.__weather_humidity.on_change()(self.__update)
        self.__humidity.on_change(pass_context=True)(self.__hysterisis)

    def __command_setpoint(self):
        if self.__auto_mode is not None:
            self.__auto_mode.value = False

    def __update(self):
        if self.__setpoint.value == 1.0:
            self.__setpoint.value = 0.5

        setpoint = self.__setpoint.value   
        if self.__auto_mode and self.__auto_mode.value:
            if self.__sleeping and self.__sleeping.value:
                setpoint = 0.65
            else:
                setpoint = 0.55
        if self.__overheat and self.__overheat.value:
            if setpoint < 0.65 and self.__weather_humidity.value > 0.7:
                setpoint = 0.65
            else:
                setpoint = max(setpoint, self.__weather_humidity.value)
        if self.__auto_mode and self.__auto_mode.value:
            self.__setpoint.update = setpoint

        self.__regulator.power.value = self.__setpoint.value != 0.0
        self.__regulator.setpoint = max(0.3, setpoint)

    def __hysterisis(self, _, humidity):
        self.__regulator.hysterisis(humidity)

    @property
    def humidity(self):
        return self.__humidity.property

    @property
    def setpoint(self):
        return self.__setpoint

    @property
    def energized(self):
        return self.__regulator.energized
