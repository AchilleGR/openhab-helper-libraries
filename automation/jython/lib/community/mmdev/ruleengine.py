import uuid
import random
import contextlib
import core.log
from functools import wraps
from core.log import log_traceback

from . import log
from . import utils
from . import prop
from . import rules


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
        def decorator(function):
            @rules.cron('%s * * ? * * *' % self.__seconds_index)
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Loop triggered'):
                    return function(*args, **kwargs)
            return function
        return decorator

    def every_day(self, hour, minute, trace=None):
        def decorator(function):
            @rules.rule('0 %s %s ? * * *' % (minute, hour))
            @log_traceback
            @wraps(function)
            def outer(*args, **kwargs):
                with self.__tracer(trace, 'Every day timer triggered'):
                    return function(*args, **kwargs)
            return function
        return decorator

    def on_weekdays(self, hour, minute, trace=None):
        def decorator(function):
            @core.oh.rules.rule('0 %s %s ? * MON,TUE,WED,THU,FRI *' % (minute, hour))
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Weekdays timer triggered'):
                    return function(*args, **kwargs)
            return function
        return decorator

    def on_weekends(self, hour, minute, trace=None):
        def decorator(function):
            @rules.rule('0 %s %s ? * SAT,SUN *' % (minute, hour))
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Weekends timer triggered'):
                    return function(*args, **kwargs)
            return function
        return decorator
            
    def on_change(self, prop, pass_context=False, null_context=False, trace=None):
        def decorator(function):
            @rules.on_change(prop.item, pass_context, null_context)
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Changed: ' + prop.item):
                    return function(*args, **kwargs)
            return function
        return decorator

    def on_command(self, prop, pass_context=False, trace=None):
        def decorator(function):
            @rules.on_command(prop.item, pass_context)
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Command: ' + prop.item):
                    return function(*args, **kwargs)
            return function
        return decorator
            

    def on_update(self, prop, pass_context=False, trace=None):
        def decorator(function):
            @rules.on_update(prop.item, pass_context)
            @log_traceback
            @wraps(function)
            def wrapper(*args, **kwargs):
                with self.__tracer(trace, 'Update: ' + prop.item):
                    return function(*args, **kwargs)
            return function
        return decorator
