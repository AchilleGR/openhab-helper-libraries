from core.log import log_traceback, getLogger
from community.mmdev.devices.thermostat import Thermostat
from community.mmdev.devices.portableac import PortableAC
from community.mmdev.manager import manager
from community.mmdev.devices.dehumidifier import Dehumidifier
from community.mmdev.devices.motiondetector import MotionDetector
from community.mmdev.devices.light import Light
from community.mmdev.devices.purifier import Purifier
from community.mmdev.devices.lock import Lock

LOGGER = getLogger('USER')
with manager() as functions:
    device, state = functions

    tvoc = state(
        int, 'TVOC', default=0,
        metadata={'ga': ('Sensor', {
            'sensorName': 'VolatileOrganicCompounds',
            'valueUnit': 'PARTS_PER_MILLION'
        })},
        channel='mqtt:topic:sensor_station:tvoc'
    )

    def mode(name, default, channel=None):
        return state(
            bool, name.replace(' ', ''), default=default, 
            channel=channel,
            metadata={'ga': ('Switch', {
                'roomHint': 'Controls',
                'name': name
            })}
        )

    def scene(name, default):
        return state(
            bool, name.replace(' ', ''), default=default,
            metadata={'ga': ('Scene', {'name': name})}
        )

    sleeping = scene('Sleep Mode', False)
    awake = scene('Awake Mode', False)
    
    @awake.on_change(pass_context=True)
    def awake_change(new):
        if new:
            sleeping.command = False

    @sleeping.on_change(pass_context=True)
    def sleeping_change(new):
        if new:
            awake.command = False


    auto_light = mode('Automatic Light Management', True)
    auto_humidity = mode('Automatic Humidity Management', True)
    auto_purify = mode('Automatic Air Purification', True)
    auto_ac = mode('Automatic Thermostat Management', True)
    overheat = mode('Overheat', default=False, channel='mqtt:topic:overheat:overheat')
    overcool = mode('Overcool', default=False, channel='mqtt:topic:overcool:overcool')

    auto_color_temp = state(
        int, 'AutomaticColorTemperature', default=6500,
        channel="mqtt:topic:color_temperature:kelvin"
    )

    auto_brightness = state(
        float, 'AutomaticBrightness', default=6500,
        channel="mqtt:topic:color_temperature:brightness"
    )

    def light(room, name, group=False, has_motion=False):
        if has_motion:
            detector = device(
                device_class=MotionDetector,
                room_name=room,
                device_name='Motion Detector',
                motion_detection_channel="hue:0107:primary:motionsensors_" + room.replace(' ', '').lower() + ":presence"
            ).motion_detected
        else:
            detector = None
        return device(
            device_class=Light,
            room_name=room,
            device_name=name,
            color_channel="hue:" + ('group' if group else '0210') + ":primary:bulbs_" + room.replace(' ', '').lower() + ":color",
            color_temperature_abs_channel="hue:"+ ('group' if group else '0210') + ":primary:bulbs_" + room.replace(' ', '').lower() + ":color_temperature_abs",
            motion_detection=detector,
            auto_mode=auto_light,
            auto_temperature=auto_color_temp,
            auto_brightness=auto_brightness,
            sleeping=sleeping
        )

    light('Living Room', 'Lights', True, True)
    light('Hallway', 'Light', True, True)
    light('Bathroom', 'Lights', True, True)
    light('Bedroom', 'Light', False, False)
    light('Bedside', 'Lamp', False, False)
    light('Closet', 'Light', True, False)

    LOGGER.error('Creating purifiera')
    def purifier(room_name, device_name):
        return device(
            device_class=Purifier,
            room_name=room_name,
            device_name=device_name,
            sleeping=sleeping,
            auto_mode=auto_purify,
            tvoc=tvoc,
            pm25_channel='mqtt:topic:' + room_name.replace(' ', '').lower() + '_air_purifier:pm25',
            fan_speed_channel='mqtt:topic:' + room_name.replace(' ', '').lower() + '_air_purifier:fan_speed'
        )

    purifier('Living Room', 'Air Purifier')
    purifier('Bedroom', 'Air Purifier')


    LOGGER.error('Creating dehumidifier')
    dehumidifier = device(
        device_class=Dehumidifier,
        room_name='Living Room',
        device_name='Dehumidifier',
        weather_humidity_channel='openweathermap:weather-and-forecast:api:local:current#humidity',
        humidity_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:sensor_relhumidity',
        energized_channel='tplinksmarthome:hs300:powerstrip_air:outlet6#switch',
        auto_mode=auto_humidity,
        sleeping=sleeping,
        overheat=overheat
    )

    LOGGER.error('Creating portableac')
    portableac = device(
        device_class=PortableAC,
        room_name='Bedroom',
        device_name='Portable AC',
        energized_channel='tplinksmarthome:hs103:portableac:switch',
        overheat=overheat
    )

    LOGGER.error('Creating thermostat')
    thermostat = device(
        device_class=Thermostat,
        device_name='Thermostat',
        room_name='Living Room',
        sleeping=sleeping,
        temperature_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:sensor_temperature',
        humidity_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:sensor_relhumidity',
        dehumidifier_energized=dehumidifier.energized,
        fan_mode_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:thermostat_fanmode',
        setpoint_low_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:thermostat_setpoint_heating',
        setpoint_high_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:thermostat_setpoint_cooling',
        portableac_energized=portableac.energized, 
        mode_channel='zwave:honeywell_th6320zw_00_000:controller:thermostat:thermostat_mode',
        auto_mode=auto_ac,
        overheat=overheat,
        overcool=overcool
    )

    LOGGER.error('Creating lock')
    lock = device(
        device_class=Lock,
        room_name='Hallway',
        device_name='Front Door Lock',
        lock_channel='mqtt:topic:front_door_lock:locked'
    )

    LOGGER.error('Done')
