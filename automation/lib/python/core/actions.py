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
from core.loader import load


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
for action in {'Audio', 'BusEvent', 'CoreUtil', 'Ephemeris', 'Exec', 'HTTP', 'Ping', 'ScriotExecution', 'Semantics', 'Things', 'Timer', 'Transformation', 'TransformationException', 'Voice'}:
    value = load(name)
    if value is not None:
        STATIC_IMPORTS.append(value)


Log = load(
    'org.openhab.core.model.script.actions.Log',
    'org.openhab.core.model.script.actions.LogAction'
)
LogAction = Log
STATIC_IMPORTS.append(Log)
STATIC_IMPORTS.append(LogAction)


for action in STATIC_IMPORTS:
    name = str(action.simpleName)
    setattr(_MODULE, name, action)
    __all__.append(name)
