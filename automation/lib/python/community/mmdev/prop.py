import core.util.items
from . import log
from core.items import add_item
from core.log import log_traceback
from core.links import remove_all_links, add_link
from core.metadata import remove_metadata, set_metadata
import time


class Prop(object):

    @log_traceback
    def __init__(self, 
                 item_type, item_name,
                 rule_engine=None,
                 default=None,
                 force=False,
                 normalize=False,
                 channel=None,
                 metadata=None,
                 groups=None,
                 logger=log.LOGGER):

        if groups is None:
            groups = set()

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
        if not core.util.items.exists(self.__item):
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

            # If normalizing/denormalizing, swap the numeric rype.
            if normalize:
                if item_type == int:
                    oh_type = 'Dimmer'
                elif item_type == float:
                    oh_type = 'Number'
                
            item = add_item(item_name, item_type=oh_type, groups=','.join(sorted(groups)))
            if not item:
                raise Exception('Failed to create ' + str(item_name) + ' as ' + str(oh_type) + ' ' + str(item_type))
            self.__logger.error('Created: ' + item_name)

            if default is not None:
                self.command(default)

            try:
                remove_all_links(item)
                if channel:
                    add_link(item, channel)
            except:
                pass

        if channel is not None:
            self.__links[item_name] = channel
        
        if metadata is not None:
            remove_metadata(item_name)
            for namespace, values in metadata.items():
                value, configuration = values
                set_metadata(
                    item_name,
                    namespace,
                    configuration,
                    value,
                    overwrite=True
                )

        self.__rule_engine.loop()(self.__relink)

    def __relink(self):
        for item, channel in self.__links.items():
            try:
                remove_all_links(item)
                add_link(item, channel)
            except:
                pass
                    
    @property
    def value(self):
        v = core.util.items.value(self.__item, default=self.__default)
        if self.__normalize and self.__item_type == int:
            return max(0.0, min(100.0, 100.0 * v))
        if self.__normalize and self.__item_type == float:
            return max(0.0, min(1.0, v / 100.0))
        return v
        
    @value.setter
    def value(self, value):
        self.command(value, force=self.__force)

    def command(self, value, force=False):
        if self.__normalize and self.__item_type == int:
            core.util.items.command(self.__item, max(0.0, min(1.0, value / 100.0)), force=force)
        elif self.__normalize and self.__item_type == float:
            core.util.items.command(self.__item, max(0.0, min(100.0, value * 100.0)), force=force)
        else:
            core.util.items.command(self.__item, value, force=force)

    def update(self, value, force=False):
        if self.__normalize and self.__item_type == int:
            core.util.items.update(self.__item, max(0.0, min(1.0, value / 100.0)), force=force)
        elif self.__normalize and self.__item_type == float:
            core.util.items.update(self.__item, max(0.0, min(100.0, value * 100.0)), force=force)
        else:
            core.util.items.update(self.__item, value, force=force)

    def on_change(self, pass_context=False, null_context=False, trace=None):

        if pass_context and self.__normalize:

            def decorator(function):
                @self.__rule_engine.on_change(
                    self,
                    pass_context=pass_context, 
                    null_context=null_context, 
                    trace=trace
                )
                def wrapper(old, new):
                    if old is not None and self.__item_type == int:
                        old = max(0.0, min(100.0, old * 100))
                    if old is not None and self.__item_type == float:
                        old = max(0.0, min(1.0, old / 100.0))
                    if new is not None and self.__item_type == int:
                        new = max(0.0, min(100.0, new * 100))
                    if old is not None and self.__item_type == float:
                        new = max(0.0, min(1.0, new / 100.0))
                    return function(old, new)
                return wrapper
            return decorator
        else:
            return self.__rule_engine.on_change(
                self,
                pass_context=pass_context, 
                null_context=null_context, 
                trace=trace
            )

    def on_deactivate(self, trace=None):
        def decorator(func):
            def wrapper(old, new):
                if not new and old:
                    func()

            return wrapper
        
        return lambda func: self.on_change(trace=trace)(decorator(func))

    def on_activate(self, trace=None):
        def decorator(func):
            def wrapper(old, new):
                if not old and new:
                    func()

            return wrapper
        
        return lambda func: self.on_change(trace=trace)(decorator(func))

    def on_command(self, pass_context=False, trace=None):
        if pass_context and self.__normalize:

            def decorator(function):
                @self.__rule_engine.on_command(
                    self, 
                    pass_context=pass_context,
                    trace=trace
                )
                def wrapper(command):
                    if command is not None and self.__normalize and self.__item_type == int:
                        return function(max(0.0, min(100.0, command * 100.0)))
                    elif command is not None and self.__normalize and self.__item_type == float:
                        return function(max(0.0, min(1.0, command / 100.0)))
                    else:
                        return function(command)
                return wrapper
            return decorator
                    
        return self.__rule_engine.on_command(
            self, 
            pass_context=pass_context,
            trace=trace
        )

    def on_update(self, pass_context=False, trace=None):
        if pass_context and self.__normalize:
            def decorator(function):
                @self.__rule_engine.on_update(
                    self,
                    pass_context=pass_context,
                    trace=trace
                )
                def wrapper(update):
                    if update is not None and self.__normalize and self.__item_type == int:
                        return function(max(0.0, min(100.0, update * 100.0)))
                    elif update is not None and self.__normalize and self.__item_type == float:
                        return function(max(0.0, min(1.0, update / 100.0)))
                    else:
                        return function(update)
                return wrapper
            return decorator
                    
        return self.__rule_engine.on_update(
            self, 
            pass_context=pass_context,
            trace=trace
        )

    def __follow_command(self, command):
        self.command(command)

    def __follow_update(self, update):
        self.update(update)
    
    def follow(self, item):
        item.on_command(
            pass_context=True
        ) (
            self.__follow_command
        )

        item.on_update(
            pass_context=True
        ) (
            self.__follow_update
        )

    @property
    def value_type(self):
        return core.util.items.item_type(self.__item)

    @property
    def trace(self):
        return self.__trace

    @trace.setter
    def trace(self, value):
        self.__trace = value
        if value:
            if not self.__trace_registered:
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
        return self.__item
