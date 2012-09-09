'''
Created on 25-08-2012

@author: jurek
'''


def get_values_as_map(_object, with_none=False, excluded_names=None):
    values = {}
    for name in filter(lambda n: not n.startswith('__'), dir(_object)):
        if excluded_names is not None and name in excluded_names:
            continue
        value = getattr(_object, name)
        if value == None and with_none == False:
            continue
        values[name] = value
    return values


def initialize_fields(_object, default_value=None):
    for name in filter(lambda n: not n.startswith('__'), dir(_object)):
        try:
            setattr(_object, name, default_value)
        except AttributeError:
            pass
