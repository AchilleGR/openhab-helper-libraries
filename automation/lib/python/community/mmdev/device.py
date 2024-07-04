from . import log
from . import prop


class Device(object):
    def __init__(self, device_collection, device_class, device_name, room_name, logger=log.LOGGER, **kwargs):
        self.device_collection = device_collection
        self.device_class = device_class
        self.logger = logger
        self.room_name = room_name
        self.device_name = device_name
        self.__property_args = kwargs

    @property
    def item_basename(self):
        return '%s_%s_%s' % (
            self.device_class.name, 
            self.room_name,
            self.device_name
        )
    
    @property
    def properties(self):
        prefix_name = '%s_' % self.item_basename

        for item in sorted(items.keys()):
            if item.startswith(prefix_name):
                yield (
                    item[prefix_name:], 
                    self.__property(item[prefix_name:])
                )

    def property(self, property_name, default=None, force=False, normalize=False):
        if self.device_collection == 'Builtin':
            item = '%s_%s_%s_%s' % (
                self.device_class.name,
                self.room_name,
                self.device_name,
                property_name
            )
        else:
            item = '%s_%s_%s_%s_%s' % (
                self.device_collection,
                self.device_class.name,
                self.room_name,
                self.device_name,
                property_name
            )
        return prop.Prop(
            item,
            default=default,
            logger=self.logger,
            force=force,
            normalize=normalize,
            **self.__property_args
        )

def State(state_name, rule_engine, default=None, force=False, **kwargs):
    return prop.Prop(
        'State_%s' % state_name, 
        rule_engine=rule_engine,
        default=default,
        force=force,
        **kwargs
    )
