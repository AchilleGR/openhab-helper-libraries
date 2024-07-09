"""
Defines a rule trigger that triggers a rule when the script loads, including
system startup.
"""
scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleFactories")


STARTUP_MODULE_ID = "jsr223.StartupTrigger"
try:
    import core
    core.STARTUP_MODULE_ID = STARTUP_MODULE_ID
    from core.log import getLogger
    LOG = getLogger("core.StartupTrigger")
except:
    LOG = None


try:
    from org.openhab.core.automation.handler import TriggerHandler
except:
    from org.eclipse.smarthome.automation.handler import TriggerHandler


class _StartupTriggerHandlerFactory(TriggerHandlerFactory):

    class Handler(TriggerHandler):

        def __init__(self, trigger):
            self.trigger = trigger

        def setCallback(self, callback):
            from threading import Timer
            start_timer = Timer(1, lambda: callback.triggered(self.trigger, {'startup': True}))
            start_timer.start()

        def dispose(self):
            pass

    def get(self, trigger):
        return self.Handler(trigger)

    def ungetHandler(self, module, rule_uid, handler):
        pass

    def dispose(self):
        pass


def scriptLoaded(script):
    automationManager.addTriggerHandler(STARTUP_MODULE_ID, _StartupTriggerHandlerFactory())
    if LOG:
        LOG.info("TriggerHandler added '{}'".format(STARTUP_MODULE_ID))

    automationManager.addTriggerType(TriggerType(
        STARTUP_MODULE_ID, None,
        "System started or rule saved",
        "Triggers when the rule is added, which occurs when the system has started or the rule has been saved",
        None, Visibility.VISIBLE, None))
    if LOG:
        LOG.info("TriggerType added '{}'".format(STARTUP_MODULE_ID))


def scriptUnloaded():
    automationManager.removeHandler(STARTUP_MODULE_ID)
    automationManager.removeModuleType(STARTUP_MODULE_ID)
    if LOG:
        LOG.info("TriggerType and TriggerHandler removed")
