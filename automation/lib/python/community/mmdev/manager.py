from functools import wraps
from contextlib import contextmanager

from core.items import remove_item
from core.util.items import all_items
from prop import Prop

from core.log import log_traceback
import configuration
from ruleengine import RuleEngine
from log import LOGGER
from device import Device


class Manager(object):
    def __init__(self,
                 logger=LOGGER,
                 rule_engine=None,
                 **kwargs):

        self.__logger = logger
        self.__extra_kwargs = kwargs
        self.__cached_devices = {}
        self.__cached_states = {}
        self.__cached_groups = {}
        self.__device_wrappers = set()

        self.__rule_engine = rule_engine
        if self.__rule_engine is None:
            self.__rule_engine = RuleEngine(
                logger=logger
            )

    def __cached_device(self, device_collection, device_class, room_name, device_name, **kwargs):
        if device_collection == 'Builtin':
            full_name = '%s_%s_%s' % (
                device_class.name, 
                room_name.replace(' ', ''),
                device_name.replace(' ', '')
            )
        else:
            full_name = '%s_%s_%s_%s' % (
                device_collection,
                device_class.name, 
                room_name.replace(' ', ''), 
                device_name.replace(' ', '')
            )

        if full_name in self.__cached_devices:
            return self.__cached_devices[full_name]

        d=Device(
            device_collection,
            device_class,
            device_name=device_name,
            room_name=room_name,
            rule_engine=self.__rule_engine,
            logger=self.__logger
        )
        cached_device = device_class(device=d, **kwargs)

        self.__device_wrappers.add(d)
                
        self.__cached_devices[full_name] = cached_device
        return full_name, cached_device

    @log_traceback
    def device_for(self, device_class, device_collection='Builtin', room_name=None, device_name=None, suppress_rules=True, **kwargs):
        return self.__cached_device(
            device_collection=device_collection,
            device_class=device_class,
            room_name=room_name,
            device_name=device_name,
            **kwargs
        )

    @log_traceback
    def state_for(self, state_type, state_name,
              default=None,
              force=False, channel=None,
              normalize=False, metadata=None):

        full_name = 'State_' + state_name
        if full_name in self.__cached_states:
            return full_name, self.__cached_states[full_name]

        cached = Prop(
            state_type, full_name,
            default=default,
            logger=self.__logger,
            force=force,
            channel=channel,
            normalize=normalize,
            metadata=metadata,
            rule_engine=self.__rule_engine
        )
        
        self.__cached_states[full_name] = cached
        return full_name, cached

    @log_traceback
    def group_for(self, group_name, metadata=None):
        group_item = 'Group_' + group_name
        if group_item in self.__cached_groups:
            return self.__cached_groups[group_item]
        group = prop.Prop(
            set, group_item,
            metadata=metadata,
            logger=self.__logger,
            rule_engine=self.rule_engine
        )
        self.__cached_groups[group_item] = group
        return group

    @log_traceback
    def cleanup(self):
        items = set()
        for d in self.__device_wrappers:
            for i in d.items:
                items.add(i)

        for s in self.__cached_states.keys():
            items.add(s)

        for g in self.__cached_groups.keys():
            items.add(g)

        for i in all_items():
            if i not in items:
                try:
                    remove_item(i)
                    self.__logger.error('Removed: ' + str(i))
                except:
                    pass

    @property
    def rule_engine(self):
        return self.__rule_engine


@contextmanager
def manager():
    m = Manager()

    @wraps(m.device_for)
    @log_traceback
    def device_wrapper(*args, **kwargs):
        return m.device_for(*args, **kwargs)[1]

    @wraps(m.state_for)
    @log_traceback
    def state_wrapper(*args, **kwargs):
        return m.state_for(*args, **kwargs)[1]

    try:
        yield device_wrapper, state_wrapper
    except Exception as e:
        @log_traceback
        def trace():
            raise e
        trace()
    finally:
        m.cleanup()
