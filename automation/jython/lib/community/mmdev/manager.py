from functools import wraps
from contextlib import contextmanager
from core.items import remove_item, add_item
from items import exists, value, command
from prop import Prop
from core.log import log_traceback
from ruleengine import RuleEngine
from log import LOGGER
from device import Device, details, as_device, translate_camel

import time


class Manager(object):
    def __init__(self,
                 logger=LOGGER,
                 rule_engine=None,
                 **kwargs):

        timestamp = time.time()
        while not exists('MMDEV_BOOT'):
            if time.time() - timestamp > 60:
                try:
                    add_item('MMDEV_BOOT', item_type='Number')
                except:
                    pass
            time.sleep(0.5)

        while value('MMDEV_BOOT') is None and time.time() - timestamp < 120:
            time.sleep(0.5)

        elapsed = time.time() - timestamp
        command('MMDEV_BOOT', elapsed, force=True)

        self.__logger = logger
        self.__extra_kwargs = kwargs
        self.__cached_devices = {}
        self.__cached_states = {}
        self.__cached_groups = {}

        self.__rule_engine = rule_engine
        if self.__rule_engine is None:
            self.__rule_engine = RuleEngine(
                logger=logger
            )

    @log_traceback
    def device_for(self, device_class, room_name, device_name, **kwargs):
        device_collection, class_name = details(device_class)
        if device_collection == 'Builtin':
            full_name = 'MMDEV_%s_%s_%s' % (
                class_name,
                room_name.replace(' ', ''),
                device_name.replace(' ', '')
            )
        else:
            full_name = 'MMDEV_%s_%s_%s_%s' % (
                device_collection,
                class_name, 
                room_name.replace(' ', ''), 
                device_name.replace(' ', '')
            )

        if full_name in self.__cached_devices:
            return self.__cached_devices[full_name]

        d=Device(
            device_class=device_class,
            device_name=device_name,
            room_name=room_name,
            rule_engine=self.__rule_engine,
            logger=self.__logger
        )
        cached_device = device_class(device=d, **kwargs)
        self.__cached_devices[full_name] = cached_device
        return cached_device

    @log_traceback
    def state_for(self, state_type, state_name,
              default=None,
              force=False, channel=None,
              normalize=False, metadata=None):

        full_name = 'MMDEV_State_' + state_name
        if full_name in self.__cached_states:
            return self.__cached_states[full_name]

        cached = Prop(
            state_type, full_name,
            default=default,
            logger=self.__logger,
            force=force,
            channel=channel,
            normalize=normalize,
            metadata=metadata,
            rule_engine=self.__rule_engine,
            property_name=state_name
        )
        
        self.__cached_states[full_name] = cached
        return cached

    @log_traceback
    def group_for(self, group_name, metadata=None):
        group_item = 'MMDEV_Group_' + group_name
        if group_item in self.__cached_groups:
            return self.__cached_groups[group_item]
        group = prop.Prop(
            set, group_item,
            metadata=metadata,
            logger=self.__logger,
            rule_engine=self.rule_engine,
            property_name=group_name
        )
        self.__cached_groups[group_item] = group
        return group

    def ephemeral_for(self, room_name, device_name):

        @as_device
        def Ephemeral(device):
            return {}

        class EphemeralDevice(object):
            def __init__(*args, **kwargs):
                self, args = args[0], args[1:]
                self.__device = Device(*args, **kwargs)
            
            def property(*args, **kwargs):
                self, args = args[0], args[1:]
                return self.__device.property(*args, **kwargs)

            @log_traceback
            def __getattr__(self, attrib):
                for p, v in self.__device.properties.items():
                    if attrib in {p, translate_camel(p)}:
                        return v
                raise AttributeError()

        return EphemeralDevice(
            room_name=room_name, 
            device_class=Ephemeral, 
            device_name=device_name, 
            rule_engine=self.rule_engine
        )

    @property
    def rule_engine(self):
        return self.__rule_engine

    @property
    def logger(self):
        return self.__logger
