DEVICE_OFFSETS = {}


def walk_dict(d, *path):
    if len(path) == 0:
        return d
    entry = path[0]
    path = path[1:]
    if entry in d:
        return walk_dict(d[entry], *path)


def get_offset(device_class, room_name, device_name, field):
    offset = walk_dict(DEVICE_OFFSETS, device_class.name, room_name, device_name, field)
    if offset is None:
        return 0.0
    return offset
