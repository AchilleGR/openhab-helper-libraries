import uuid
import random
import contextlib
import core.log
import core.util.rules
from core.log import log_traceback

from . import log
from . import utils
from . import prop


class RuleEngine(object):
    def __init__(self, logger=log.LOGGER):
        self.__logger = logger
        self.__seconds_index = random.randint(0, 59)

    def __log(level, msg):
        if level.upper() == 'WARNING':
            self.__logger.warn(msg)
        elif level.upper() == 'DEBUG':
            self.__logger.debug(msg)
        elif level.upper() == 'ERROR':
            self.__logger.error(msg)
        elif level.upper() == 'CRITICAL':
            self.__logger.crit(msg)
        else:
            self.__logger.info(msg)

    @contextlib.contextmanager
    def __tracer(self, trace, trace_msg):
        if trace is not None:
            self.__log(trace, 'TRACE: %s' % (trace_msg))
        yield

    def loop(self, trace=None):
        self.__seconds_index = (self.__seconds_index + 13) % 60
        def decorator(func):
            func = log_traceback(func)
            core.util.rules.cron('%s * * ? * * *' % self.__seconds_index)(func)
            return func
        return decorator

    def every_day(self, hour, minute, trace=None):
        def wrapper(func):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Every day timer triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.util.rules.rule('0 %s %s ? * * *' % (minute, hour))(wrapper(func))

    def on_weekdays(self, hour, minute, trace=None):
        def wrapper(outer):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Weekdays timer triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.oh.rules.rule('0 %s %s ? * MON,TUE,WED,THU,FRI *' % (minute, hour))(wrapper(func))

    def on_weekends(self, hour, minute, trace=None):
        def wrapper(func):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Weekends timer triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.util.rules.rule('0 %s %s ? * SAT,SUN *' % (minute, hour))(wrapper(func))

    def on_change(self, prop, pass_context=False, null_context=False, trace=None):
        def wrapper(func):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Change watch triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.util.rules.on_change(prop.item, pass_context, null_context)(wrapper(func))

    def on_command(self, prop, pass_context=False, trace=None):
        def wrapper(func):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Command watch triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.util.rules.on_command(prop.item, pass_context)(wrapper(func))

    def on_update(self, prop, pass_context=False, trace=None):
        def wrapper(func):
            @log_traceback
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Update watch triggered'):
                    return func(*args, **kwargs)
            return outer
            
        return lambda func: core.util.rules.on_update(prop.item, pass_context)(wrapper(func))
