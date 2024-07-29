from . import log
from . import prop


class Device(object):
    def __init__(self, device_collection, device_class, device_name, room_name, rule_engine, logger=log.LOGGER):
        self.device_collection = device_collection
        self.device_class = device_class
        self.logger = logger
        self.room_name = room_name
        self.device_name = device_name
        self.rule_engine = rule_engine
        self.__items = set()

    @property
    def items(self):
        return self.__items

    def property(self, property_type, property_name, channel=None, default=None, force=False, normalize=False, metadata=None, groups=None):
        if self.device_collection == 'Builtin':
            item = '%s_%s_%s_%s' % (
                self.device_class.name,
                self.room_name.replace(' ', ''),
                self.device_name.replace(' ', ''),
                property_name
            )
        else:
            item = '%s_%s_%s_%s_%s' % (
                self.device_collection,
                self.device_class.name,
                self.room_name.replace(' ', ''),
                self.device_name,
                property_name
            )
        self.__items.add(item)
        return prop.Prop(
            property_type, item,
            default=default,
            logger=self.logger,
            force=force,
            channel=channel,
            normalize=normalize,
            metadata=metadata,
            groups=groups,
            rule_engine=self.rule_engine
        )

    def group(self, group_name, metadata=None):
        group_item = 'Group_' + group_name
        self.__items.add(group_item)
        return prop.Prop(
            set, group_item,
            metadata=metadata,
            rule_engine=self.rule_engine
        )
