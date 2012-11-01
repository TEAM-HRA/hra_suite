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


def get_other_keys(_dict, keys):
    keys = [key for key in _dict if key not in keys]
    return keys[0] if len(keys) == 1 else keys


def get_any_key(**_dict):
    """ a method to get all keys as a list or
        if there is only one key returns that key  """
    keys = [key for key in _dict]
    return keys[0] if len(keys) == 1 else keys
