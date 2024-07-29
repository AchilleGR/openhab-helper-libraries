class Purifier(object):
    collection='Builtin'
    name='Purifier'

    def __init__(self, device,
                 pm25_channel=None,
                 fan_speed_channel=None,
                 tvoc=None,
                 sleeping=None,
                 auto_mode=None):

        self.__tvoc = tvoc
        self.__auto_mode = auto_mode
        self.__sleeping = sleeping

        self.__pm25 = device.property(
            int, 'PM25', default=0.0,
            channel=pm25_channel,
            metadata={'ga': ('Sensor', {
                'name': device.device_name + ' Dust Sensor',
                'roomHint': device.room_name,
                'sensorName': 'PM2.5',
                'valueUnit': 'MICROGRAMS_PER_CUBIC_METER'
            })}
        )

        self.__auto_fan_speed = device.property(
            float, 'AutomaticFanSpeed', default=0.0
        )

        self.__manual_fan_speed = device.property(
            float, 'ManualFanSpeed', default=0.0,
            metadata={'ga': ('AirPurifier', {
                'name': device.device_name,
                'roomHint': device.room_name,
                'lang': 'en',
                'speeds': '0=Off,25=Slow,50=Medium,75=Fast,100=Max',
                'ordered': True
            })}
        )

        self.__real_fan_speed = device.property(
            float, 'RealFanSpeed', default=0.0,
            channel=fan_speed_channel
        )

        if self.__tvoc:
            self.__tvoc.on_change()(self.__update)
        self.__pm25.on_change()(self.__update)
        if self.__auto_mode:
            self.__auto_mode.on_change()(self.__update)
        if self.__sleeping:
            self.__sleeping.on_change()(self.__update) 
        self.__manual_fan_speed.on_command()(self.__manual_command)

    @property
    def pm25(self):
        return self.__pm25

    @property
    def automatic_fan_speed(self):
        return self.__auto_fan_speed

    @property
    def manual_fan_speed(self):
        return self.__manual_fan_speed

    @property
    def fan_speed(self):
        return self.__real_fan_speed

    def __manual_command(self):
        if self.__auto_mode:
            self.__auto_mode.value = False
        self.__update()

    def __update(self):
        
        tvoc = 0
        if self.__tvoc:
            tvoc = self.__tvoc.value

        air_quality_perc = 1.0 - max(0.0, min(1.0, (self.__pm25.value - 5.0) / 20.0))
        tvoc_ppm_perc = 1.0 - max(0.0, min(1.0, tvoc / 12000.0))

        fan_speed = 1.0 - min(tvoc_ppm_perc, air_quality_perc)
        self.__auto_fan_speed.value = fan_speed

        if not self.__auto_mode.value:
            self.__real_fan_speed.value = self.__manual_fan_speed.value
        else:
            if self.__sleeping.value:
                self.__real_fan_speed.value = min(0.33, fan_speed)
            else:
                self.__real_fan_speed.value = fan_speed
            self.__manual_fan_speed.update = self.__real_fan_speed.value
