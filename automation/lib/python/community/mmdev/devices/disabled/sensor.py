from .. import device


class Sensor(object):
    collection='Builtin'
    name = 'Sensor'
    def __init__(self, device_class, room_name, device_name, property_name, logger, default=0.0, normalize=False, transform=None, **kwargs):
        dev = device.Device(
            device_class=device_class,
            room_name=room_name,
            device_name=device_name,
            logger=logger,
            **kwargs
        )

        self.__property = dev.property(
            property_name, 
            default=default,
            normalize=normalize
        )

        self.__real_property = dev.property(
            'Real' + property_name, 
            default=default
        )

        self.__logger = logger
        self.__normalize = normalize
        self.__transform = transform

        if self.__real_property.exists:
            self.__update()

    def register(self):
        if self.__real_property.exists:
            self.__real_property.on_change()(self.__update)

    def __update(self):
        field = self.__property
        rfield = self.__real_property
        value = rfield.value
        if field.value_type == 'Number' and rfield.value_type == 'Dimmer':
            if self.__normalize:
                value = int(rfield.value)
            else:
                value = int(rfield.value * 100.0)
        elif field.value_type == 'Dimmer' and rfield.value_type == 'Number':
            if self.__normalize:
                value = rfield.value / 10000.0
            else:
                value = rfield.value / 100.0
        elif self.__normalize:
            value = rfield.value / 100.0

        if self.__transform is not None:
            value = self.__transform(value)
        
        field.value = value

    @property
    def property(self):
        return self.__property
