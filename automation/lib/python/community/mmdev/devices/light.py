from core.jsr223.scope import QuantityType, events, itemRegistry
from org.openhab.core.library.unit import Units


class Light(object):
    collection='Builtin'
    name='Light'

    def __init__(self, device, 
                 color_channel=None, 
                 color_temperature_abs_channel=None, 
                 motion_detection=None, 
                 auto_mode=None,
                 auto_temperature=None,
                 auto_brightness=None,
                 sleeping=None):

        self.__real_color = device.property(
            tuple, 'RealColor', default=(0,0,0), force=True, 
            channel=color_channel
        )

        self.__device_name = device.device_name

        self.__manual_color = device.property(
            tuple, 'ManualColor', default=(0,0,0),
            metadata={'ga': ('Light', {
                'roomHint': device.room_name,
                'name': device.device_name,
                'colorTemperatureRange': '2000,6500'
            })}
        )

        self.__real_color_temperature_abs = device.property(
            int, 'RealColorTemperatureAbs', default=2000, force=True,
            channel=color_temperature_abs_channel
        )

        self.__manual_color_temperature_abs = device.property(
            int, 'ManualColorTemperatureAbs', default=2000, force=True
        )

        self.__manual_using_temp = device.property(
            bool, 'ManualUsingTemp', default=True
        )

        self.__motion_detection = motion_detection
        self.__auto_mode = auto_mode
        self.__auto_temperature = auto_temperature
        self.__auto_brightness = auto_brightness
        self.__sleeping = sleeping

        self.__room_name = device.room_name
        self.__logger = device.logger
        self.__off_trigger = False

        if self.__motion_detection:
            self.__motion_detection.on_command()(self.__update)
        if self.__auto_temperature:
            self.__auto_temperature.on_change()(self.__update)
        if self.__auto_brightness:
            self.__auto_brightness.on_change()(self.__update)
        if self.__auto_mode:
            self.__auto_mode.on_change()(self.__update)

        self.__manual_color.on_command(
            pass_context=True
        ) (
            self.__color_command
        )

        self.__update()

    def __color_command(self, command, update=False):
        if not update:
            if self.__auto_mode.value:
                self.__manual_color.update = self.__real_color.value
                self.__manual_color_temperature_abs.update = self.__real_color_temperature_abs.value
                self.__manual_using_temp.update = True
            self.__auto_mode.value = False

        if isinstance(command, tuple) or isinstance(command, list):
            if not update:
                self.__manual_using_temp.value = False
            new_h, new_s, _ = command
            _, _, old_b = self.__manual_color.value
            self.__manual_color.value = (new_h, new_s, old_b)

        elif isinstance(command, float):
            old_h, old_s, _ = self.__manual_color.value
            self.__manual_color.value = (old_h, old_s, command)

        elif isinstance(command, bool):
            old_h, old_s, _ = self.__manual_color.value
            self.__manual_color.value = (old_h, old_s, 1.0 if command else 0.0)

        self.__update()

    def __update(self):
        if self.__auto_mode and self.__auto_mode.value:
            if self.__auto_brightness:
                brightness = max(0.01, self.__auto_brightness.value)
            else:
                brightness = 1.0
            if self.__room_name in ['Bathroom']:
                if self.__sleeping and self.__sleeping.value:
                    brightness=0.5
                else:
                    brightness=max(0.33,brightness)
            if self.__auto_temperature:
                temp = self.__auto_temperature.value
            else:
                temp = 6500
            if temp < 2000.0:
                temp = 2000.0
            elif temp > 6500.0:
                temp = 6500.0
            
            power = (
                (self.__motion_detection and self.__motion_detection.value )
                or (self.__sleeping and not self.__sleeping.value)
                or self.__room_name in ['Bathroom']
            )
    
            try:
                events.sendCommand(itemRegistry.getItem(self.__real_color_temperature_abs.item), QuantityType(temp, Units.KELVIN))
            except:
                events.sendCommand(itemRegistry.getItem(self.__real_color_temperature_abs.item), QuantityType(max(2200, temp, Units.KELVIN)))

            if power:
                self.__real_color.value = brightness
            else:
                self.__real_color.value = False
            self.__manual_color.update = self.__real_color.value
            self.__manual_color_temperature_abs.update = self.__real_color_temperature_abs.value
        else:
            if self.__manual_using_temp:
                self.__real_color_temperature_abs.value = self.__manual_color_temperature_abs.value
            else:
                self.__real_color.value = self.__manual_color.value

