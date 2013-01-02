'''
Created on 25-08-2012

@author: jurek
'''
import re


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


def get_keys_for_value(_dict, _value, _regexpr=False, _one_key_only=False):

    ## Method returns all keys of a dictionary which have values as passed
    #  value or as regular expression value
    #  @param _dict: a dictionary
    #  @param _value: a value for comparison
    #  @param _regexpr: if is True value parameter is treated as
    #          a regular expression
    #  @param _one_key_only: if is True only one key is returned
    value_re = re.compile(_value) if _regexpr else None
    _keys = [key for key, value in _dict.items()
             if value == _value or (value_re and value_re.search(value))]
    if len(_keys) > 0:
        return _keys[0] if _one_key_only else _keys


def get_for_regexpr(_iterable, _regexpr):

    ## Method which returns all items of iterable which correspond
    #  to regular expression
    #  @param _iterable: an iterable
    #  @param _regexpr: a regular expression
    if _iterable and _regexpr:
        compiled_re = re.compile(_regexpr) if _regexpr else None
        return [value for value in _iterable if compiled_re.search(value)]


def replace_all_by_dict(_string, _dict):

    ## Method which replaces all occurrences of dictionary keys
    #  which are presented in a string in a form of '{dictionary key}'
    #  by corresponding dictionary values
    #  @param _string: a string to be replaced
    #  @param _dict: a dictionary of identifiers and values
    if _string and _dict and len(_dict) > 0:
        for key, value in _dict.items():
            _string = _string.replace("{" + key + "}", value)
    return _string


def create_list(element, size):
    return [element for _ in range(size)]


def empty_string(value):
    return "" if value == None else str(value)
