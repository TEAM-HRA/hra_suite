'''
Created on 25-08-2012

@author: jurek
'''
import re


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
    """
    create a list consists of one element and specified size
    """
    return [element for _ in range(size)]


def empty_string(value):
    return "" if value == None else str(value)


def any_indexes(iterable):
    """
    returns all indexes for items in iterable for which items are true
    """
    if iterable:
        return [idx for idx, item in enumerate(iterable) if item == True]


def or_values(iterable):
    if iterable:
        if len(iterable) == 0:
            return None
        elif len(iterable) >= 1:
            value = iterable[0]
            for num, _iter in enumerate(iterable):
                if num > 0:
                    value = value | _iter
            return value


def all_true_values(_object, _names):
    """
    check if all members of passed _object has value True
    """
    for name in _names:
        if hasattr(_object, name):
            if getattr(_object, name, False) == False:
                return False
        else:
            return False
    return True


def nvl(*iterable):
    """
    returns first not None value in collection
    """
    for _iter in iterable:
        if not _iter == None:
            return _iter


def get_subdict(_dict, keys=None, not_keys=None):
    """
    function which returns sub dict of _dict dictionary
    with specified keys or without not_keys
    """
    d = _dict
    if keys:
        d = dict([(key, d[key]) for key in d if key in keys])
    if not_keys:
        d = dict([(key, d[key]) for key in d if key not in not_keys])
    return d


def get_namedtuple_fields_as_list(_named_tuple):
    return list(_named_tuple._fields) if _named_tuple else None


def get_as_list(_string, separator=',', strip_spaces=True):
    """
    convert a string into a list divided by a specified separator
    """
    return [name.strip(' ') if strip_spaces else name
                for name in _string.split(separator)]
