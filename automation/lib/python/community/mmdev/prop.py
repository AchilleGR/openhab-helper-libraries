from . import log
from .oh import items


class Prop(object):
    def __init__(self,
                 item_name,
                 rule_engine,
                 default=None,
                 force=False,
                 normalize=False,
                 logger=log.LOGGER):

        self.__item = item_name
        self.__default = default
        self.__force = force
        self.__rule_engine = rule_engine
        self.__logger = logger
        self.__normalize = normalize
        self.__trace = False
        self.__trace_registered = False

    @property
    def item(self):
        return self.__item
    
    @property
    def exists(self):
        return items.item_exists(self.__item)

    @property
    def value(self):
        if self.__normalize:
            return items.item(self.__item, default=self.__default) / 100.0
        else:
            return items.item(self.__item, default=self.__default)
        
    @value.setter
    def value(self, value):
        self.command(value, force=self.__force)

    def command(self, value, force=False):
        if self.exists:
            if self.__normalize:
                items.command(self.__item, value * 100.0, force=force)
            else:
                items.command(self.__item, value, force=force)

    def update(self, value, force=False):
        if self.exists:
            if self.__normalize:
                items.update(self.__item, value * 100.0, force=force)
            else:
                items.update(self.__item, value, force=force)

    def on_change(self, pass_context=False, null_context=False, trace=None):
        if self.exists:
            return self.__rule_engine.on_change(
                self,
                pass_context=pass_context,
                null_context=null_context,
                trace=trace
            )
        else:
            return lambda func: func

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
        if self.exists:
            return self.__rule_engine.on_command(
                self, 
                pass_context=pass_context,
                trace=trace
            )
        else:
            return lambda func: func

    def on_update(self, pass_context=False, trace=None):
        if self.exists:
            return self.__rule_engine.on_update(
                self, 
                pass_context=pass_context,
                trace=trace
            )
        else:
            return lambda func: func

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
        if not self.exists:
            return None

        return items.item_type(self.__item)

    @property
    def trace(self):
        return self.__trace

    @trace.setter
    def trace(self, value):
        self.__trace = value
        if not self.exists:
            return
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
