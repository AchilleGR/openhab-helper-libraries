from core.exceptions import suppress
from . import log
from . import items
from core.items import add_item, remove_item
from core.log import log_traceback
from core.links import remove_all_links, add_link, ITEM_CHANNEL_LINK_REGISTRY
from core.metadata import remove_metadata, set_metadata, get_all_namespaces
import time
import json
from functools import wraps
from community.mmdev.log import LOGGER

from core.jsr223.scope import things

_BOOT = time.time()

try:
    from org.openhab.core.thing import ChannelUID
except:
    from org.eclipse.smarthome.core.thing import ChannelUID

class Prop(object):

    def __init__(self, 
                 item_type, item_name,
                 rule_engine=None,
                 default=None,
                 force=False,
                 normalize=False,
                 channel=None,
                 metadata=None,
                 groups=set(),
                 dimension=None,
                 property_name = None,
                 proxy=None,
                 logger=log.LOGGER):

        self.__property_name = property_name
        self.channel = channel
        self.__dimension = dimension
        self.__groups = groups
        self.metadata = metadata
        self.__item_type = item_type
        self.__links = dict()
        self.__item = item_name
        self.__default = default
        self.__force = force
        self.__rule_engine = rule_engine
        self.__logger = logger
        self.__normalize = normalize
        self.__trace = False
        self.__trace_registered = False
        self.__proxy = proxy
        if item_type == int:
            oh_type = 'Number'
        elif item_type == float:
            oh_type = 'Dimmer'
        elif item_type == bool:
            oh_type = 'Switch'
        elif item_type == tuple:
            oh_type = 'Color'
        elif item_type == set:
            oh_type = 'Group'
        elif item_type == str:
            oh_type = 'String'
        else:
            parts = item_type.split(':')
            oh_type = parts[0]
            if len(parts) > 1:
                self.__dimension = parts[1]

        if normalize:
            if item_type == int:
                oh_type = 'Dimmer'
            elif item_type == float:
                oh_type = 'Number'

        self.__oh_type = oh_type
        self.__logger = logger

        if proxy is None:
            rule_engine.loop()(self.__ensure_item)
            try:
               self.__ensure_item()
            except:
                pass

    @property
    def property_name(self):
        return self.__property_name

    @property
    def __full_type(self):
        if self.__dimension is None:
            return self.__oh_type
        return '%s:%s' % (self.__oh_type, self.__dimension)

    @log_traceback
    def __ensure_item(self):

        now = time.time()

        if not items.exists(self.__item) and now - _BOOT < 60:
            return

        def create():
            add_item(self.__item, item_type=self.__full_type, groups=[g.item for g in self.__groups])
            log.LOGGER.info('Created: ' + self.__item)
            self.command = self.__default

        if not items.exists(self.__item):
            create()

        elif items.item_type(self.__item) != self.__oh_type or items.item_dimension(self.__item) != self.__dimension:
            remove_item(self.__item)
            create()

        if self.__default is not None:
            if items.value(self.__item) is None:
                if now - _BOOT < 60 * 2:
                    return
                self.command = self.__default

        try:
            has_channel = (
                self.channel is not None 
                and things.getChannel(ChannelUID(self.channel)) is not None
            )
        except Exception as e:
            LOGGER.error('Failed to cast channel: %s' % self.channel)
            raise e

        channels = [
            str(c)
            for c 
            in ITEM_CHANNEL_LINK_REGISTRY.getBoundChannels(self.__item)
        ]

        replace = (
            (not has_channel and len(channels) > 0)
            or (has_channel and (len(channels) != 1 or channels[0] != self.channel))
        )

        if replace:
            remove_all_links(self.__item)
            if has_channel:
                add_link(self.__item, self.channel)

        metadata = {}
        if self.metadata is not None:
            metadata = json.loads(json.dumps(self.metadata))
        if metadata is None:
            metadata = {}
        metadata['mmdev'] = (str(time.time()), {})

        for namespace in get_all_namespaces(self.__item):
            if namespace not in metadata:
                remove_metadata(self.__item, namespace)

        for namespace, values in metadata.items():
            value, configuration = values
            set_metadata(
                self.__item,
                namespace,
                configuration,
                value,
                overwrite=True
            )

    def __wait_for_item(self):
        while not self.exists:
            time.sleep(0.5)
    
    @property
    def exists(self):
        if self.__proxy is not None:
            return self.__proxy.exists

        return items.exists(self.__item)

    @property
    def value(self):
        if self.__proxy is not None:
            return self.__proxy.value

        self.__wait_for_item()
        v = items.value(self.__item, default=self.__default)
        if v is None:
            return None
        if self.__normalize and self.__item_type == int:
            return max(0.0, min(100.0, v * 100.0))
        if self.__normalize and self.__item_type == float:
            return max(0.0, min(1.0, v / 100.0))
        return v
        
    @property
    def command(self):
        if self.__proxy is not None:
            return self.__proxy.command

        def commander(value, force=self.__force):
            self.__wait_for_item()
            if self.__normalize and self.__item_type == int:
                items.command(
                    self.__item, max(0.0, min(100.0, value * 100.0)), 
                    force=force
                )
            elif self.__normalize and self.__item_type == float:
                items.command(
                    self.__item, max(0.0, min(1.0, value / 100.0)), 
                    force=force
                )
            else:
                items.command(
                    self.__item, value, 
                    force=force
                )
        return commander

    @command.setter
    def command(self, value):
        return self.command(value)
        
    @property
    def update(self):
        if self.__proxy is not None:
            return self.__proxy.update

        def updater(value, force=self.__force):
            self.__wait_for_item()
            if self.__normalize and self.__item_type == int:
                items.update(
                    self.__item, max(0.0, min(100, value * 100.0)), 
                    force=force
                )
            elif self.__normalize and self.__item_type == float:
                items.update(
                    self.__item, max(0.0, min(1.0, value / 100.0)), 
                    force=force
                )
            else:
                items.update(
                    self.__item, value, 
                    force=force
                )
        return updater

    @update.setter
    def update(self, value):
        return self.update(value)

    def on_change(self, pass_context=False, null_context=False, trace=None):
        if self.__proxy is not None:
            return self.__proxy.on_change(
                pass_context=pass_context,
                null_context=null_context,
                trace=trace
            )

        self.__wait_for_item()
        def decorator(function):
            @self.__rule_engine.on_change(
                self,
                pass_context=True,
                trace=trace
            )
            @wraps(function)
            def wrapper(old, new):
                if not pass_context:
                    return function()

                if old is not None and self.__item_type == int:
                    old = max(0.0, min(100.0, old * 100))
                elif old is not None and self.__item_type == float:
                    old = max(0.0, min(1.0, old / 100.0))
                if new is not None and self.__item_type == int:
                    new = max(0.0, min(100.0, new * 100))
                elif new is not None and self.__item_type == float:
                    new = max(0.0, min(1.0, new / 100.0))
                    if null_context or (old is not None and new is not None):
                        return function(old, new)
                
            return function
        return decorator

    def on_deactivate(self, trace=None):
        if self.__proxy is not None:
            return self.__proxy.on_deactivate(
                trace=trace
            )

        self.__wait_for_item()
        def decorator(function):
            @self.on_command(
                pass_context=True, 
                trace=trace
            )
            @wraps(function)
            def wrapper(value):
                if not value:
                    return function()
            return function
        return decorator
        
    def on_activate(self, trace=None):
        if self.__proxy is not None:
            return self.__proxy.on_activate(
                trace=trace
            )

        def decorator(function):
            @self.on_command(
                pass_context=True, 
                null_context=False,
                trace=trace
            )
            @wraps(function)
            def wrapper(value):
                if value:
                    return function()
            return function
        return decorator

        
    def on_command(self, pass_context=False, null_context=False, trace=None):
        if self.__proxy is not None:
            return self.__proxy.on_command(
                pass_context=pass_context, 
                null_context=null_context,
                trace=trace
            )

        self.__wait_for_item()
        def decorator(function):
            @self.__rule_engine.on_command(
                self,
                pass_context=True,
                trace=trace
            )
            @wraps(function)
            def wrapper(command):
                if not pass_context:
                    return function()
                if command is not None and self.__normalize and self.__item_type == int:
                    return function(max(0.0, min(100.0, command * 100.0)))
                elif command is not None and self.__normalize and self.__item_type == float:
                    return function(max(0.0, min(1.0, command / 100.0)))
                elif null_context or command is not None:
                    return function(command)

            return function
        return decorator

    def on_update(self, pass_context=False, null_context=False, trace=None):
        if self.__proxy is not None:
            return self.__proxy.on_update(
                pass_context=pass_context,
                null_context=null_context,
                trace=trace
            )

        self.__wait_for_item()
        def decorator(function):
            @self.__rule_engine.on_update(
                self,
                pass_context=True,
                trace=trace
            )
            @wraps(function)
            def wrapper(update):
                if not pass_context:
                    return function()
                if update is not None and self.__normalize and self.__item_type == int:
                    return function(max(0.0, min(100.0, update * 100.0)))
                elif update is not None and self.__normalize and self.__item_type == float:
                    return function(max(0.0, min(1.0, update / 100.0)))
                elif null_context or (update is not None):
                    return function(update)

            return function
        return decorator

    @property
    def sync(self):
        if self.__proxy is not None:
            return self.__proxy.sync

        def syncer(prop):

            @prop.on_command(pass_context=True)
            def prop_command(value):
                self.command(value)

            @self.on_command(pass_context=True)
            def self_command(value):
                prop.command(value)

            self.command = prop.value

        return syncer

    @sync.setter
    def sync(self, prop):
        return self.sync(prop)

    @property
    def follow(self):
        if self.__proxy is not None:
            return self.__proxy.follow

        def follower(prop, force=self.__force):
            self.__wait_for_item()
            try:
                self.command = prop.value
            except:
                pass

            @prop.on_command(pass_context=True)
            def on_command(value):
                self.command(value, force=force)

            @prop.on_update(pass_context=True)
            def on_update(value):
                self.update(value, force=force)

        return follower

    @follow.setter
    def follow(self, prop):
        return self.follow(prop)

    @property
    def invert(self):
        if self.__proxy is not None:
            return self.__proxy.invert

        def inverter(prop, force=self.__force):

            @prop.on_command(pass_context=True)
            def on_command(value):
                if not isinstance(value, bool):
                    self.command(not value, force=force)

            @prop.on_update(pass_context=True)
            def on_update(_, value):
                if isinstance(value, bool):
                    self.update(not value, force=force)

        return inverter

    @invert.setter
    def invert(self, prop):
        return self.invert(prop)

    @property
    def value_type(self):
        if self.__proxy is not None:
            return self.__proxy.value_type

        self.__wait_for_item()
        return items.item_type(self.__item)

    @property
    def trace(self):
        if self.__proxy is not None:
            return self.__proxy.trace

        return self.__trace

    @trace.setter
    def trace(self, value):
        if self.__proxy is not None:
            self.__proxy.trace = value
            return

        self.__trace = value
        if value:
            if not self.__trace_registered:
                self.__wait_for_item()
                self.__trace_registered = True
                self.on_change(pass_context=True, null_context=True)(self.__trace_change)
                self.on_command(pass_context=True)(self.__trace_command)
                self.on_update(pass_context=True)(self.__trace_update)

    def __trace_change(self, old, new):
        if self.__trace:
            self.__logger.error('TRACE: Change: %s => %s -> %s' % (old, new, self.__item))

    def __trace_command(self, command):
        if self.__trace:
            self.__logger.error('TRACE: Command: %s -> %s' % (command, self.__item))

    def __trace_update(self, update):
        if self.__trace:
            self.__logger.error('TRACE: Update: %s -> %s' % (update, self.__item))

    @property
    def item(self):
        if self.__proxy is not None:
            return self.__proxy.item

        return self.__item
