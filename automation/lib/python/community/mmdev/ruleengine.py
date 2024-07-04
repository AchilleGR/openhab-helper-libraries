import uuid
import random
import contextlib
import core.log

from . import log
from .oh import items
from .oh import rules
from .oh import types
from . import utils
from . import prop


class RuleEngine(object):
    def __init__(self, logger=log.LOGGER):
        self.__logger = logger
        self.__seconds_index = random.randint(0, 59)
        self.__loops = 0
        self.__changes = 0
        self.__commands = 0
        self.__updates = 0
        self.__crons = 0
        self.__trace = False

    def __performance_tracer(self):
        num = self.__events
        max_num = self.__events_concurrent_max
        self.__events = 0
        self.__events_concurrent_max = 0
        self.__events_concurrent = 0.0
        self.__events_last_minute.value = num
        num = num / 60.0
        self.__burst_ratio.value = float(max_num) / max(float(num), 1.0)
        self.__load_average_5.value = self.__events_sampler_5(num)
        self.__load_average_10.value = self.__events_sampler_10(num)
        self.__load_average_15.value = self.__events_sampler_15(num)

    @contextlib.contextmanager
    def __tracer(self, trace_msg, trace):
        if trace is not None:
            self.__logger.error(
                'TRACE: %s: %s' % (
                    trace_msg, trace
                )
            )
            
        if self.__trace:
            self.__events += 1
            self.__events_concurrent += 1
            if self.__events_concurrent > self.__events_concurrent_max:
               self.__events_concurrent_max = self.__events_concurrent 
            try:
                yield
            finally:
                self.__events_concurrent -= 1
                if self.__events_concurrent < 0:
                    self.__events_concurrent = 0
        else:
            yield

    def status(self):
        self.__logger.error('Rule Engine: %s loops, %s change listeners, %s command listeners, %s update listeners, %s cron jobs' % (self.__loops, self.__changes, self.__commands, self.__updates, self.__crons))

    def loop(self, trace=None):
            
        self.__loops += 1
        self.__seconds_index = (self.__seconds_index + 13) % 60
        def wrapper(func):
            def outer():
                with self.__tracer('Loop timer triggered', trace):
                    return func()
            return outer
            
        return lambda func: rules.cron('%s * * ? * * *' % self.__seconds_index)(wrapper(func))

    def every_day(self, hour, minute, trace=None):
        self.__crons += 1

        def wrapper(func):
            def outer():
                with self.__tracer('Every day timer triggered', trace):
                    return func()
            return outer
            
        return lambda func: rules.rule('0 %s %s ? * * *' % (minute, hour))(wrapper(func))

    def on_weekdays(self, hour, minute, trace=None):
        self.__crons += 1

        def wrapper(outer):
            def outer():
                with self.__tracer('Weekdays timer triggered', trace):
                    return func()
            return outer
            
        return lambda func: rules.rule('0 %s %s ? * MON,TUE,WED,THU,FRI *' % (minute, hour))(wrapper(func))

    def on_weekends(self, hour, minute, trace=None):
        self.__crons += 1

        def wrapper(func):
            def outer():
                with self.__tracer('Weekends timer triggered', trace):
                    return func()
            return outer
            
        return lambda func: rules.rule('0 %s %s ? * SAT,SUN *' % (minute, hour))(wrapper(func))

    def on_change(self, prop, pass_context=False, null_context=False, trace=None):
        self.__changes += 1

        def wrapper(func):
            def outer(*args):
                with self.__tracer('Change watch triggered', trace):
                    return func(*args)
            return outer
            
        return lambda func: rules.on_change(prop.item, pass_context, null_context)(wrapper(func))

    def on_command(self, prop, pass_context=False, trace=None):
        self.__commands += 1

        def wrapper(func):
            def outer(*args):
                with self.__tracer('Command watch triggered', trace):
                    return func(*args)
            return outer
            
        return lambda func: rules.on_command(prop.item, pass_context)(wrapper(func))

    def on_update(self, prop, pass_context=False, trace=None):
        self.__updates += 1

        def wrapper(func):
            def outer(*args):
                with self.__tracer('Update watch triggered', trace):
                    return func(*args)
            return outer
            
        return lambda func: rules.on_update(prop.item, pass_context)(wrapper(func))

    def performance_trace(self):
        if not self.__trace:
            self.__burst_ratio = prop.Prop(item_name='State_BurstRatio', rule_engine=self, default=1.0)
            self.__events_last_minute = prop.Prop(item_name='State_EventsLastMinute', rule_engine=self, default=0.0)
            self.__load_average_5 = prop.Prop(item_name='State_LoadAverage5', rule_engine=self, default=0.0)
            self.__load_average_10 = prop.Prop(item_name='State_LoadAverage10', rule_engine=self, default=0.0)
            self.__load_average_15 = prop.Prop(item_name='State_LoadAverage15', rule_engine=self, default=0.0)
            self.__load_average_10 = prop.Prop('State_LoadAverage10', self, default=0.0)
            self.__events_sampler_5 = utils.sampler(self.__load_average_5.value, 5)
            self.__events_sampler_10 = utils.sampler(self.__load_average_10.value, 10)
            self.__events_sampler_15 = utils.sampler(self.__load_average_15.value, 15)
            self.__events = 0
            self.__events_concurrent_max = 0.0
            self.__events_concurrent = 0.0
            self.__trace = True
            self.loop()(self.__performance_tracer)
