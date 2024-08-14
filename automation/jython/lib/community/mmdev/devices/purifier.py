from .. import device


@device.as_device
def Purifier(device):

    tvoc = device.property(int, 'TVOC', default=0)
    automatic_mode = device.property(bool, 'AutomaticMode', default=0)
    automatic_speed = device.property(bool, 'AutomaticSpeed', default=0)
    pm25 = device.property(int, 'PM25', default=0)
    sleeping = device.property(bool, 'Sleeping', default=False)

    automatic_fan_speed = device.property(
        float, 'AutomaticFanSpeed', default=0.0
    )

    controls = device.property(
        float, 'Controls', default=0.0
    )

    fan_speed = device.property(
        float, 'FanSpeed', default=0.0
    )
    
    @automatic_mode.on_activate()
    def automatic_mode_activated():
        automatic_speed.command = True

    @fan_speed.on_command()
    def manual_command():
        automatic_speed.command = False
        automatic_mode.command = False

    @tvoc.on_change()
    @pm25.on_change()
    @automatic_speed.on_change()
    @sleeping.on_change()
    @fan_speed.on_change()
    @controls.on_change()
    def update():
        
        air_quality_perc = 1.0 - max(0.0, min(1.0, (pm25.value - 5.0) / 20.0))
        tvoc_ppm_perc = 1.0 - max(0.0, min(1.0, tvoc.value / 12000.0))

        speed = max(0, 1.0 - min(tvoc_ppm_perc, air_quality_perc))
        automatic_fan_speed.command = speed

        if not automatic_speed.value:
            fan_speed.command = controls.value
            return

        if sleeping.value:
            speed = min(0.33, speed)
        if speed < 0.05:
            speed = 0
        fan_speed.command = speed
        controls.update = speed

    return {
        automatic_fan_speed,
        automatic_mode,
        controls,
        fan_speed,
        pm25,
        sleeping,
        tvoc
    }
