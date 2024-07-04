from . import airqualitymonitor
from . import dehumidifier
from . import huedimmer
from . import humidifier
from . import hygrometer
from . import light
from . import lock
from . import motiondetector
from . import occupancydetector
from . import outlet
from . import purifier
from . import thermometer
from . import thermostat
from . import bedjet

MMDEV_COLLECTION = 'Builtin'

MMDEV_CLASSES = set([
    airqualitymonitor.AirQualityMonitor,
    dehumidifier.Dehumidifier,
    huedimmer.HueDimmer,
    humidifier.Humidifier,
    hygrometer.Hygrometer,
    light.Light,
    lock.Lock,
    motiondetector.MotionDetector,
    occupancydetector.OccupancyDetector,
    outlet.Outlet,
    purifier.Purifier,
    thermometer.Thermometer,
    thermostat.Thermostat,
    bedjet.BedJet
])
