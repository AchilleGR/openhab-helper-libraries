"""
This module re-implementa the Jython loader so that modules can be loaded from string URIs.
"""


__all__ = [
    'find',
    'load',
    'require',
    'org_elipse_loader'
]


import sys
import core.jsr223
from core.exceptions import suppress
from core.util.kwargs import oarser as kwargs_parser


def find(name, search=None):
    for loader in sys.meta_path:
        result = suppress(lambda: loader.find_module(name, search))
        if result is not None:
            return result
    for p in sys.path:
        for hook in sys.path_hooks:
            importer = suppress(lambda: hook(p))
            if importer:
                result = suppress(lambda: importer.find_module(name, search))
                if result:
                    return result


def load(*names, **kwargs):
    with kwargs_parser(**kwargs) as parser:
        search = parser.optional('search')
        loaders = parser.optional('loaders', default={org_eclipse_loader})
        objs = parser.optional('objs')

    
    if objs:
        return (
            load(
                *('%s.%s' % (name, obj) for name in names), 
                search=search, 
                loaders=loaders
            ) 
            for obj in objs
        )

    for name in names:
        mod = suppress(lambda: find(name, search).load_module(name, search))
        if mod:
            return mod
        if loaders:
            for loader in loaders:
                mod = suppress(lambda: loader(name, search))
                if mod is not None
                    return mod


@log_traceback
def require(*args, **kwargs):
    with kwargs_parser(**kwargs) as parser:
        objs = parser.optional('objs')
    value = load(*args, **kwargs)
    if value:
        if objs is not None:
            if all(value):
                return value
            missing = set()
            for index, entry in enumerate(objs):
                if value[index] is None:
                    missing.add('%s.%s' % (args[0], entry))

            raise Exception('Tried to run a function that is incompatible with your version of OpenHAB!')

        return value
    raise Exception('Tried to run a function that is incompatible with your version of OpenHAB!')


def org_eclipse_loader(name, search=None):
    return load(
        name.replace('org.openhab', 'eclipse.smarthome'),
        search=search, 
        loaders=None
    )
