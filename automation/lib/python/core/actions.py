"""
This module discovers action services registered from OH1 or OH2 bundles or
add-ons. The specific actions that are available will depend on which add-ons
are installed. Each action class is exposed as an attribute of the
``core.actions`` module. The action methods are static methods on those classes
(don't try to create instances of the action classes).

.. warning:: In order to avoid namespace conflicts with the ``actions`` object
    provided in the default scope, don't use ``import core.actions`` or
    ``from core import actions``.

See the :ref:`Guides/Actions:Actions` guide for details on the use of this
module.
"""
import sys
from core import osgi


__all__ = []


OH1_ACTIONS = osgi.find_services("org.openhab.core.scriptengine.action.ActionService", None) or []
OH2_ACTIONS = osgi.find_services("org.openhab.core.model.script.engine.action.ActionService", None) or osgi.find_services("org.eclipse.smarthome.model.script.engine.action.ActionService", None) or []

_MODULE = sys.modules[__name__]

for action in OH1_ACTIONS + OH2_ACTIONS:
    action_class = action.actionClass
    name = str(action_class.simpleName)
    setattr(_MODULE, name, action_class)
    __all__.append(name)


STATIC_IMPORTS = []


try:
    from org.openhab.core.model.script.actions import Audio
    STATIC_IMPORTS.append(Audio)
except:
    pass
try:
    from org.openhab.core.model.script.actions import BusEvent
    STATIC_IMPORTS.append(BusEvent)
except:
    pass
try:
    from org.openhab.core.model.script.actions import CoreUtil
    STATIC_IMPORTS.append(CoreUtil)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Ephemeris
    STATIC_IMPORTS.append(Ephemeris)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Exec
    STATIC_IMPORTS.append(Exec)
except:
    pass
try:
    from org.openhab.core.model.script.actions import HTTP
    STATIC_IMPORTS.append(HTTP)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Log
    LogAction = Log
except:
    try:
        # OH2 post ESH merge
        from org.openhab.core.model.script.actions import LogAction
        Log = LogAction
    except:
        # OH2 pre ESH merge
        from org.eclipse.smarthome.model.script.actions import LogAction
        Log = LogAction
STATIC_IMPORTS.append(Log)
STATIC_IMPORTS.append(LogAction)
try:
    from org.openhab.core.model.script.actions import Ping
    STATIC_IMPORTS.append(Ping)
except:
    pass
try:
    from org.openhab.core.model.script.actions import ScriptExecution
    STATIC_IMPORTS.append(ScriptExecution)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Semantics
    STATIC_IMPORTS.append(Semantics)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Things
    STATIC_IMPORTS.append(Things)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Timer
    STATIC_IMPORTS.append(Timer)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Transformation
    STATIC_IMPORTS.append(Transformation)
except:
    pass
try:
    from org.openhab.core.model.script.actions import TransformationException
    STATIC_IMPORTS.append(TransformationException)
except:
    pass
try:
    from org.openhab.core.model.script.actions import Voice
    STATIC_IMPORTS.append(Voice)
except:
    pass


for action in STATIC_IMPORTS:
    name = str(action.simpleName)
    setattr(_MODULE, name, action)
    __all__.append(name)
