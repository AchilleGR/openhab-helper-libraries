# pylint: disable=eval-used
"""
This trigger can respond to file system changes. For example, you could watch a
directory for new files and then process them.
"""
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY
from org.openhab.core.automation.handler import TriggerHandler
from org.openhab.core.service import WatchServiceFactory

import core
from core.log import getLogger, log_traceback

LOG = getLogger("core.DirectoryEventTrigger")
core.DIRECTORY_TRIGGER_MODULE_ID = "jsr223.DirectoryEventTrigger"

scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")


class JythonDirectoryWatcher(object):

    def __init__(self, path, event_kinds=[ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY], watch_subdirectories=False):
        self.path = path
        self.event_kinds = event_kinds
        self.watch_subdirectories = watch_subdirectories
        self.callback = None
        self.__watcher = None

    def deactivate(self):
        if self.__watcher is not None:
            self.__watcher.unregisterListener(self)

    def activate(self):
        if self.__watcher is not None:
            return
        self.__watcher = WatchServiceFactory.createWatchService(
            core.DIRECTORY_TRIGGER_MODULE_ID,
            self.path
        )
        self.__watcher.registerListener(self, path, self.watch_subdirectories)

    def getWatchEventKinds(self, path):
        return self.event_kinds

    def watchSubDirectories(self):
        return self.watch_subdirectories

    @log_traceback
    def processWatchEvent(self, event, kind, path):
        if kind in self.event_kinds and self.callback is not None:
            self.callback(event, kind, path)


@log_traceback
class _DirectoryEventTriggerHandlerFactory(TriggerHandlerFactory):

    @log_traceback
    class Handler(TriggerHandler):

        @log_traceback
        def __init__(self, trigger):
            TriggerHandler.__init__(self)
            self.rule_engine_callback = None
            self.trigger = trigger
            config = trigger.configuration
            self.watcher = JythonDirectoryWatcher(
                config.get('path'), 
                eval(config.get('event_kinds')),
                watch_subdirectories=config.get('watch_subdirectories')
            )
            self.watcher.callback = self.handle_directory_event
            self.watcher.activate()

        def setCallback(self, callback):
            self.rule_engine_callback = callback

        @log_traceback
        def handle_directory_event(self, event, kind, path):
            self.rule_engine_callback.triggered(self.trigger, {
                'event': event,
                'kind': kind,
                'path': path
            })

        def dispose(self):
            self.watcher.deactivate()
            self.watcher = None


    def get(self, trigger):
        return _DirectoryEventTriggerHandlerFactory.Handler(trigger)


def scriptLoaded(*args):
    automationManager.addTriggerHandler(
        core.DIRECTORY_TRIGGER_MODULE_ID,
        _DirectoryEventTriggerHandlerFactory())
    LOG.info("TriggerHandler added '{}'".format(core.DIRECTORY_TRIGGER_MODULE_ID))

    automationManager.addTriggerType(TriggerType(
        core.DIRECTORY_TRIGGER_MODULE_ID, None,
        "a directory change event is detected.",
        "Triggers when a directory change event is detected.",
        None, Visibility.VISIBLE, None))
    LOG.info("TriggerType added '{}'".format(core.DIRECTORY_TRIGGER_MODULE_ID))


def scriptUnloaded():
    automationManager.removeHandler(core.DIRECTORY_TRIGGER_MODULE_ID)
    automationManager.removeModuleType(core.DIRECTORY_TRIGGER_MODULE_ID)
    LOG.info("TriggerType and TriggerHandler removed '{}'".format(core.DIRECTORY_TRIGGER_MODULE_ID))
