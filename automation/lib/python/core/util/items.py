# Library for interacting with items in openhab.
import core.log
from core.jsr223.scope import items, itemRegistry, events
from . import types


ITEMS=items


def all():
    return set(items.keys())


def exists(item_name):
    return item_name in all()


def value(item_name, default=None):
    if not exists(item_name):
        return default
    item_obj = itemRegistry.getItem(item_name)
    if default is None:
        return types.from_type(item_obj.state)
    elif types.is_undefined(item_obj.state):
        update(item_name, default, force=True)
        return default
    else:
        return types.from_type(item_obj.state)


def item_type(item_name):
    item_obj = itemRegistry.getItem(item_name)
    return item_obj.type.split(':')[0]


def to_item_type(item_name, val):
    if val is None:
        return None
    item_obj = itemRegistry.getItem(item_name)
    state = item_obj.getState()
    item_type = item_obj.type.split(':')[0]

    if item_type == 'Number':
        return types.to_decimal(val)

    elif item_type == 'Dimmer':
        return types.to_percent(val)

    elif item_type == 'Switch':
        return types.to_onoff(val)

    elif item_type == 'Color':
        if isinstance(val, tuple) or isinstance(val, list):
            return types.to_color(val)

        elif val is True or val is False:
            return types.to_onoff(val)

        else:
            return types.to_percent(val)
        
    else:
        raise Exception('Unsupported item type: %s' % item_obj.type)


def _apply_item(item_name, val, force, action):
    item_obj = itemRegistry.getItem(item_name)
    val = to_item_type(item_name, val)
    if force:
        core.log.log_traceback(lambda: action(item_obj, val))()
    else:
        old_val = to_item_type(item_name, value(item_name))
        if not types.is_equal(val, old_val):
            core.log.log_traceback(lambda: action(item_obj, val))()


def command(item_name, val, force=False):
    _apply_item(item_name, val, force, events.sendCommand)


def update(item_name, val, force=False):
    _apply_item(item_name, val, force, events.postUpdate)
