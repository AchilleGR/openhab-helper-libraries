import uuid
import random
import contextlib
import core.log
import core.oh.rules

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
        def wrapper(func):
            def outer():
                with self.__tracer(trace, 'Loop timer triggered'):
                    return func()
            return outer
            
        return lambda func: core.oh.rules.cron('%s * * ? * * *' % self.__seconds_index)(wrapper(func))

    def every_day(self, hour, minute, trace=None):
        def wrapper(func):
            def outer():
                with self.__tracer(trace, 'Every day timer triggered'):
                    return func()
            return outer
            
        return lambda func: core.oh.rules.rule('0 %s %s ? * * *' % (minute, hour))(wrapper(func))

    def on_weekdays(self, hour, minute, trace=None):
        def wrapper(outer):
            def outer():
                with self.__tracer(trace, 'Weekdays timer triggered'):
                    return func()
            return outer
            
        return lambda func: cpre.oh.rules.rule('0 %s %s ? * MON,TUE,WED,THU,FRI *' % (minute, hour))(wrapper(func))

    def on_weekends(self, hour, minute, trace=None):
        def wrapper(func):
            def outer():
                with self.__tracer(trace, 'Weekends timer triggered'):
                    return func()
            return outer
            
        return lambda func: core.oh.rules.rule('0 %s %s ? * SAT,SUN *' % (minute, hour))(wrapper(func))

    def on_change(self, prop, pass_context=False, null_context=False, trace=None):
        def wrapper(func):
            def outer(*args):
                with self.__tracer(trace, 'Change watch triggered'):
                    return func(*args)
            return outer
            
        return lambda func: core.oh.rules.on_change(prop.item, pass_context, null_context)(wrapper(func))

    def on_command(self, prop, pass_context=False, trace=None):
        def wrapper(func):
            def outer(*args):
                with self.__tracer(trace, 'Command watch triggered'):
                    return func(*args)
            return outer
            
        return lambda func: core.oh.rules.on_command(prop.item, pass_context)(wrapper(func))

    def on_update(self, prop, pass_context=False, trace=None):
        def wrapper(func):
            def outer(*args):
                with self.__tracer(trace, 'Update watch triggered'):
                    return func(*args)
            return outer
            
        return lambda func: core.oh.rules.on_update(prop.item, pass_context)(wrapper(func))
