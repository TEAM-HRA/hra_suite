'''
Created on 25-08-2012

@author: jurek
'''


def get_values_as_map(_object, with_none=False, excluded_names=[]):
    values = {}
    for name in filter(lambda n: not n.startswith('__'), dir(_object)):
        if name not in excluded_names:
            value = getattr(_object, name, __VOID_VALUE)
            if isinstance(value, __VoidValue) and with_none == False:
                continue
            values[name] = None if isinstance(value, __VoidValue) else value
    return values


def initialize_fields(_object, default_value=None):
    for name in filter(lambda n: not n.startswith('__'), dir(_object)):
        try:
            setattr(_object, name, default_value)
        except AttributeError:
            pass


class __VoidValue(object):
    pass

__VOID_VALUE = __VoidValue()
