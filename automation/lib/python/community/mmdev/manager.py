import importlib
import core.log
import core.oh.items

import configuration

from . import ruleengine
from . import prop
from . import devices
from . import log


collections = [
    'community.mmdev.devices'
]

try:
    for collection in configuration.mmdev_collections:
        collections.append(collection)
except:
    pass

DEVICE_CLASSES = {}

for collection in collections:
    module = importlib.import_module(collection)
    DEVICE_CLASSES[module.MMDEV_COLLECTION] = set()
    for device_class in module.MMDEV_CLASSES:
        DEVICE_CLASSES[module.MMDEV_COLLECTION].add(device_class)

class Manager(object):
    def __init__(self,
                 logger=log.LOGGER,
                 rule_engine=None,
                 **kwargs):

        self.__logger = logger
        self.__extra_kwargs = kwargs
        self.__cached_devices = {}
        self.__cached_states = {}

        self.__rule_engine = rule_engine
        if self.__rule_engine is None:
            self.__rule_engine = ruleengine.RuleEngine(
                logger=logger
            )

    @property
    def rooms(self):
        already_emitted = set()
        for item_name in core.oh.items.items():
            item_name_parts = item_name.split('_')
            if len(item_name_parts) != 4:
                continue
            _, item_room, _, _ = item_name_parts
            if item_room not in already_emitted:
                already_emitted.add(item_room)
                yield item_room

    def __cached_device(self, device_collection, device_class, room_name, device_name, suppress_rules=True, **kwargs):
        full_name = '%s_%s_%s_%s' % (device_collection, device_class.name, room_name, device_name) 
        if full_name in self.__cached_devices:
            return self.__cached_devices[full_name]
        cached_device = device_class(
            device_collection=device_collection,
            room_name=room_name,
            device_name=device_name,
            rule_engine=self.__rule_engine,
            **kwargs
        )

        self.__cached_devices[full_name] = cached_device
        return cached_device

    def devices_for(self, device_class, device_collection='Builtin', room_name=None, device_name=None, suppress_rules=True):
        already_emitted = set()
        for item_name in core.oh.items.items():
            item_name_parts = item_name.split('_')
            if device_collection == 'Builtin':
                if len(item_name_parts) != 4:
                    continue
                item_type, item_room, item_device_name, _ = item_name_parts
            else:
                if len(item_name_parts) != 5:
                    continue
                item_collection, item_type, item_room, item_device_name, _ = item_name_parts
                if item_collection != device_collection:
                    continue
            if item_type != device_class.name:
                continue
            if room_name != None and room_name != item_room:
                continue
            if device_name != None and item_device_name != device_name:
                continue

            if device_collection == 'Builtin':
                item_emit_name = '%s_%s_%s' % (
                    item_type, 
                    item_room, 
                    item_device_name
                )
            else:
                item_emit_name = '%s_%s_%s_%s' % (
                    item_collection,
                    item_type, 
                    item_room, 
                    item_device_name
                )
            if item_emit_name in already_emitted:
                continue
            already_emitted.add(item_emit_name)
            cdev = core.log.log_traceback(lambda: self.__cached_device(
                device_collection=device_collection,
                device_class=device_class,
                room_name=item_room,
                device_name=item_device_name,
                logger=self.__logger,
                **self.__extra_kwargs
            ))()
            if cdev is not None:
                yield item_emit_name, cdev

    def device_for(self, device_class, room_name, device_name, device_collection='Builtin'):
        return list(self.devices_for(
            device_collection=device_collection,
            device_class=device_class,
            room_name=room_name, 
            device_name=device_name
        ))[0]

    @property
    def all_devices(self):
        for collection, classes in DEVICE_CLASSES.items():
            for device_class in classes:
                for device_name, device in self.devices_for(device_collection=collection, device_class=device_class):
                    yield device_name, device

    def initialize(self):
        for name, device in self.all_devices:
            try:
                register = device.register
            except:
                register = None

            if register is not None:
                core.log.log_traceback(lambda: register())()
        self.__rule_engine.performance_trace()

    def state_for(self, state_name, force=False, default=None, **kwargs):
        full_name = 'State_%s' % state_name 
        if full_name in self.__cached_states:
            return self.__cached_states[full_name]
        cached_state = prop.Prop(
            full_name,
            rule_engine=self.__rule_engine,
            default=default,
            force=force,
            **kwargs
        )
        self.__cached_states[full_name] = cached_state
        return full_name, cached_state

    @property
    def rule_engine(self):
        return self.__rule_engine

    def status(self):
        self.__rule_engine.status()
