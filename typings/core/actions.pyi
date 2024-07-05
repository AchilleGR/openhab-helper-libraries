# pylint: disable=unused-import

try:
    from org.openhab.core.model.script.actions import Audio
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Audio
    except:
        pass
try:
    from org.openhab.core.model.script.actions import BusEvent
except:
    try:
        from org.eclipse.smarthome.model.script.actions import BusEvent
    except:
        pass
try:
    from org.openhab.core.model.script.actions import CoreUtil
except:
    try:
        from org.eclipse.smarthome.model.script.actions import CoreUtil
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Ephemeris
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Ephemeris
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Exec
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Exec
    except:
        pass
try:
    from org.openhab.core.model.script.actions import HTTP
except:
    try:
        from org.eclipse.smarthome.model.script.actions import HTTP
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Log
except:
    try:
        # OH2 post ESH merge
        from org.openhab.core.model.script.actions import LogAction
        Log = LogAction
    except:
        # OH2 pre ESH merge
        from org.eclipse.smarthome.model.script.actions import LogAction
        Log = LogAction
try:
    from org.openhab.core.model.script.actions import Ping
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Ping
    except:
        pass
try:
    from org.openhab.core.model.script.actions import ScriptExecution
except:
    try:
        from org.eclipse.smarthome.model.script.actions import ScriptExecution
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Semantics
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Semantics
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Things
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Things
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Timer
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Timer
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Transformation
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Transformation
    except:
        pass
try:
    from org.openhab.core.model.script.actions import TransformationException
except:
    try:
        from org.eclipse.smarthome.model.script.actions import TransformationException
    except:
        pass
try:
    from org.openhab.core.model.script.actions import Voice
except:
    try:
        from org.eclipse.smarthome.model.script.actions import Voice
    except:
        pass
