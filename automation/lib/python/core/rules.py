# pylint: disable=invalid-name
"""
The rules module contains some utility functions and a decorator that can:

    1) decorate a Jython class to create a ``SimpleRule``,
    2) decorate the ``when`` function decorator to create a ``SimpleRule``.
"""
__all__ = [
    'rule',
    'addRule'
]

from inspect import isclass
from core.log import getLogger, log_traceback
from core.jsr223.scope import SimpleRule, scriptExtension


LOG = getLogger("core.rules")
scriptExtension.importPreset("RuleSimple")


def rule(name=None, description=None, tags=None):
    """
    This decorator can be used with both functions and classes to create rules.

    See :ref:`Guides/Rules:Decorators` for a full description of how to use
    this decorator.

    Examples:
        .. code-block::

          @rule('name', 'description', ['tag1', 'tag2'])
          @rule('name', tags=['tag1', 'tag2'])
          @rule('name')

    Args:
        name (str): display name of the rule
        description (str): (optional) description of the rule
        tags (list): (optional) list of tags as strings
    """
    def rule_decorator(new_rule):
        if isclass(new_rule):
            class_ = new_rule
            def init(self, *args, **kwargs):
                SimpleRule.__init__(self)
                if name is None:
                    if hasattr(class_, '__name__'):
                        self.name = class_.__name__
                    else:
                        self.name = "JSR223-Jython"
                else:
                    self.name = name
                self.log = getLogger(self.name)
                class_.__init__(self, *args, **kwargs)
                if description is not None:
                    self.description = description
                elif self.description is None and class_.__doc__:
                    self.description = class_.__doc__
                if hasattr(self, "getEventTriggers"):
                    self.triggers = log_traceback(self.getEventTriggers)()
                if tags is not None:
                    self.tags = set(tags)
            subclass = type(class_.__name__, (class_, SimpleRule), dict(__init__=init))
            subclass.execute = log_traceback(class_.execute)
            new_rule = addRule(subclass())
            subclass.UID = new_rule.UID
            return subclass
        else:
            callable_obj = new_rule
            if callable_obj.triggers.count(None) == 0:
                simple_rule = _FunctionRule(callable_obj, callable_obj.triggers, name=name, description=description, tags=tags)
                new_rule = addRule(simple_rule)
                callable_obj.UID = new_rule.UID
                callable_obj.triggers = None
                return callable_obj
            else:
                LOG.warn(u"rule: not creating rule '{}' due to an invalid trigger definition".format(name))
                return None
    return rule_decorator


class _FunctionRule(SimpleRule):
    def __init__(self, callback, triggers, name=None, description=None, tags=None):
        self.triggers = triggers
        if name is None:
            if hasattr(callback, '__name__'):
                name = callback.__name__
            else:
                name = "JSR223-Jython"
        self.name = name
        callback.log = getLogger(name)
        callback.name = name
        self.callback = callback
        if description is not None:
            self.description = description
        if tags is not None:
            self.tags = set(tags)

    @log_traceback
    def execute(self, module, inputs):
        self.callback(inputs.get('event'))


def addRule(new_rule):
    """
    This function adds a ``rule`` to openHAB's ``ruleRegistry``.

    This is a wrapper of ``automationManager.addRule()`` that does not require
    any additional imports. The `addRule` function is similar to the
    `automationManager.addRule` function, except that it can be safely used in
    modules (versus scripts). Since the `automationManager` is different for
    every script scope, the `core.rules.addRule` function looks up the
    automation manager for each call.

    Args:
        new_rule (SimpleRule): a rule to add to openHAB

    Returns:
        Rule: the Rule object that was created
    """
    LOG.debug(u"Added rule '{}'".format(new_rule.name))
    return scriptExtension.get("automationManager").addRule(new_rule)
