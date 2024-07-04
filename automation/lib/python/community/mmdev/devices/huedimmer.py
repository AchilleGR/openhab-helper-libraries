from .. import device


class HueDimmer(object):
    collection='Builtin'
    name='HueDimmer'
    def __init__(self, **kwargs):
        self.__device = device.Device(
            device_class=HueDimmer,
            **kwargs
        )

        self.__button_code_property = self.__device.property('ButtonCode')
        self.__callbacks = {}

    @property
    def button_code(self):
        return self.__button_code_property

    def __append_callback(self, code, func):
        if code not in self.__callbacks:
            self.__callbacks[code] = set()
        self.__callbacks[code].add(func)

    def on_power_on_pressed(self, func):
        self.__append_callback(1002.0, func)

    def on_power_on_held(self, func):
        self.__append_callback(1001.0, func)

    def on_power_on_released(self, func):
        self.__append_callback(1000.0, func)

    def on_brightness_up_pressed(self, func):
        self.__append_callback(2002.0, func)

    def on_brightness_up_held(self, func):
        self.__append_callback(2001, func)

    def on_brightness_up_released(self, func):
        self.__append_callback(2000.0, func)

    def on_brightness_down_pressed(self, func):
        self.__append_callback(3002.0, func)

    def on_brightness_down_held(self, func):
        self.__append_callback(3001.0, func)

    def on_brightness_down_released(self, func):
        self.__append_callback(3000.0, func)

    def on_power_off_pressed(self, func):
        self.__append_callback(4002.0, func)

    def on_power_off_held(self, func):
        self.__append_callback(4001.0, func)

    def on_power_off_released(self, func):
        self.__append_callback(4000.0, func)

    def __on_button_press(self, code):
        if code not in self.__callbacks:
            return
        for func in self.__callbacks[code]:
            func()

    def register_buttons(self):
        self.__button_code_property.on_update(
            pass_context=True
        ) (
            self.__on_button_press
        )
