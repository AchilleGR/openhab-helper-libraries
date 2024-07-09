# pylint: disable=eval-used
"""
This trigger can respond to file system changes. For example, you could watch a
directory for new files and then process them.
"""
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY

try:
    scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0
except:
    pass

try:
    from org.openhab.core.automation.handler import TriggerHandler
except:
    from org.eclipse.smarthome.automation.handler import TriggerHandler

try:
    try:
        from org.openhab.core.service import AbstractWatchService
    except:
        from org.eclipse.smarthome.core.service import AbstractWatchService
    BASE_CLASS = AbstractWatchService
    WatchServiceFactory = None
except:
    from org.openhab.core.automation.handler import TriggerHandler
    from org.openhab.core.service import WatchServiceFactory
    BASE_CLASS = object

DIRECTORY_TRIGGER_MODULE_ID = "jsr223.DirectoryEventTrigger"
try:
    import core
    core.DIRECTORY_TRIGGER_MODULE_ID = DIRECTORY_TRIGGER_MODULE_ID
    from core.log import getLogger, log_traceback
    LOG = getLogger("core.DirectoryEventTrigger")
except:
    LOG = None
    def log_traceback(func):
        return func


scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")


class JythonDirectoryWatcher(BASE_CLASS):

    def __init__(self, path, event_kinds=[ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY], watch_subdirectories=False):
        if BASE_CLASS is not object:
            BASE_CLASS.__init__(self, path)
        else:
            self.__path = path
            self.__watcher = None

        self.event_kinds = event_kinds
        self.watch_subdirectories = watch_subdirectories
        self.callback = None

    def deactivate(self):
        if self.__watcher is not None:
            self.__watcher.unregisterListener(self)
            self.__watcher = None

    def activate(self):
        if BASE_CLASS is not object or self.__watcher is not None:
            return
        self.__watcher = WatchServiceFactory.createWatchService(
            DIRECTORY_TRIGGER_MODULE_ID,
            self.__path
        )
        self.__watcher.registerListener(self, self.__path, self.watch_subdirectories)

    def getWatchEventKinds(self, path):
        return self.event_kinds

    def watchSubDirectories(self):
        return self.watch_subdirectories

    @log_traceback
    def processWatchEvent(self, event, kind, path):
        if self.callback is not None and kind in self.event_kinds:
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
                config.get('path'), eval(config.get('event_kinds')),
                watch_subdirectories=config.get('watch_subdirectories'))
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
        DIRECTORY_TRIGGER_MODULE_ID,
        _DirectoryEventTriggerHandlerFactory())
    if LOG:
        LOG.info("TriggerHandler added '{}'".format(DIRECTORY_TRIGGER_MODULE_ID))

    automationManager.addTriggerType(TriggerType(
        DIRECTORY_TRIGGER_MODULE_ID, None,
        "a directory change event is detected.",
        "Triggers when a directory change event is detected.",
        None, Visibility.VISIBLE, None))
    if LOG:
        LOG.info("TriggerType added '{}'".format(DIRECTORY_TRIGGER_MODULE_ID))


def scriptUnloaded():
    automationManager.removeHandler(DIRECTORY_TRIGGER_MODULE_ID)
    automationManager.removeModuleType(DIRECTORY_TRIGGER_MODULE_ID)
    if LOG:
        LOG.info("TriggerType and TriggerHandler removed '{}'".format(DIRECTORY_TRIGGER_MODULE_ID))
