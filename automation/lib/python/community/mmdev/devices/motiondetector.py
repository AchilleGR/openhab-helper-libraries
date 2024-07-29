import time


class MotionDetector(object):
    collection='Builtin'
    name='MotionDetector'

    def __init__(self, device,
                 motion_detection_channel=None):

        self.__last_detected = device.property(
            int, 'LastDetected', default=0.0
        )

        self.__motion_detected = device.property(
            bool, 'MotionDetected', default=False
        )

        self.__power = device.property(
            bool, 'Power', default=True
        )

        self.__timeout = device.property(
            int, 'MotionTimeout', default=150.0
        )

        self.__real_motion_detection = device.property(
            bool, 'RealMotionDetected', default=False,
            channel=motion_detection_channel
        )

        self.__real_motion_detection.on_change(
            pass_context=True
        ) (
            self.__motion_change
        )
        
        self.__power.on_change() (
            self.__update
        )
        
        device.rule_engine.loop()(
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
            self.__last_detected.value = time.time()
            self.motion_detected.value = True

    def __update(self):
        if time.time() - self.__last_detected.value > self.__timeout.value or not self.powered.value:
            self.motion_detected.value = False

