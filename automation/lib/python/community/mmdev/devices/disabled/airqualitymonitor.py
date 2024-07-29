from .. import device


class AirQualityMonitor(object):
    collection='Builtin'
    name='AirQualityMonitor'
    def __init__(self, **kwargs):

        self.__device = device.Device(
            device_class = self,
            **kwargs
        )

        self.__voc= self.__device.property(
            'VOC'
        )

        self.__voc0 = self.__device.property(
            'VOC0', 
            default=False
        )

        self.__voc25 = self.__device.property(
            'VOC25', 
            default=False
        )

        self.__voc65 = self.__device.property(
            'VOC65', 
            default=False
        )

        self.__voc100 = self.__device.property(
            'VOC100', 
            default=False
        )

        self.__cm = self.__device.property(
            'CarbonMonoxide'
        )

        self.__cm0 = self.__device.property(
            'CarbonMonoxide0', 
            default=False
        )

        self.__cm10 = self.__device.property(
            'CarbonMonoxide10', 
            default=False
        )

        self.__cm15 = self.__device.property(
            'CarbonMonoxide15',
            default=False
        )

        self.__cm50 = self.__device.property(
            'CarbonMonoxide50', 
            default=False
        )

        self.__update_cm()
        self.__update_voc()

    def register(self):
        self.__voc0.on_change() (
            self.__update_voc
        )

        self.__voc25.on_change() (
            self.__update_voc
        )

        self.__voc65.on_change() (
            self.__update_voc
        )

        self.__voc100.on_change() (
            self.__update_voc
        )

        self.__cm0.on_change() (
            self.__update_cm
        )

        self.__cm10.on_change() (
            self.__update_cm
        )

        self.__cm15.on_change() (
            self.__update_cm
        )

        self.__cm50.on_change() (
            self.__update_cm
        )

    def __update_cm(self):
        if self.__cm50.value:
            self.__cm.value = 50.0
        elif self.__cm15.value:
            self.__cm.value = 15.0
        elif self.__cm10.value:
            self.__cm.value = 10.0
        elif self.__cm0.value:
            self.__cm.value = 1.0
        else:
            self.__cm.value = 0.0

    def __update_voc(self):
        if self.__voc100.value:
            self.__voc.value = 100 * 500.0
        elif self.__voc65.value:
            self.__voc.value = 65 * 500.0
        elif self.__voc25.value:
            self.__voc.value = 25 * 500.0
        elif self.__voc0.value:
            self.__voc.value = 500.0
        else:
            self.__voc.value = 0.0

    @property
    def voc(self):
        return self.__voc

    @property
    def carbon_monoxide(self):
        return self.__carbon_monoxide
