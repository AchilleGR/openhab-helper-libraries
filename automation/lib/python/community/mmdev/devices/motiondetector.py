import time

from .. import device


class MotionDetector(object):
    collection='Builtin'
    name='MotionDetector'
    def __init__(self, rule_engine, **kwargs):
        dev = device.Device(
            device_class=MotionDetector,
            rule_engine=rule_engine,
            **kwargs
        )

        self.__last_detected = 0.0

        self.__motion_detected = dev.property(
            'MotionDetected', default=False
        )

        self.__power = dev.property(
            'Power', default=True
        )

        self.__timeout = dev.property(
            'Timeout', default=150.0
        )

        self.__real_motion_detection = dev.property('RealMotionDetected')
        self.__rule_engine = rule_engine

    def register(self):
        self.__real_motion_detection.on_change(
            pass_context=True
        ) (
            self.__motion_change
        )
        
        self.__power.on_change() (
            self.__update
        )
        
        self.__rule_engine.loop()(
            self.__update
        )

    @property
    def motion_detected(self):
        return self.__motion_detected

    @property
    def powered(self):
        return self.__power

    @property
    def timeout(self):
        return self.__timeout

    def __motion_change(self, _, new):
        if new and self.powered.value:
            self.__last_detected = time.time()
            self.motion_detected.value = True

    def __update(self):
        if time.time() - self.__last_detected > self.__timeout.value or not self.powered.value:
            self.motion_detected.value = False

