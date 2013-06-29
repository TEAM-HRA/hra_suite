'''
Created on 25-08-2012

@author: jurek
'''
import re


def get_other_keys(_dict, keys):
    keys = [key for key in _dict if key not in keys]
    if len(keys) == 1:
        return keys[0]
    elif len(keys) > 1:
        return keys


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


def get_as_list(_string, separator=',', strip_characters=' '):
    """
    convert a string into a list divided by a specified separator
    """
    if not _string == None:
        return [name.strip(strip_characters)
            if not strip_characters == None else name
                for name in _string.split(separator)]


def not_empty_nvl(*iterable):
    """
    returns first not None and not empty value in collection
    """
    for _iter in iterable:
        if not _iter == None and len(str(_iter)) > 0:
            return _iter


def get_as_tuple(_string, separator=',', strip_characters=' ', convert=None):
    """
    convert a string divided by a specified separator into a tuple
    """
    if isinstance(_string, tuple):
        return _string
    if _string is not None:
        _list = get_as_list(_string, separator, strip_characters)
        return tuple(_list if convert == None else map(convert, _list))


def commas(*iterable, **params):
    """
    method used to join iterable by comma;
    """

    #if iterable has only one element of string type then
    #change it into iterable with element of list type
    #to avoid splitting the string by a comma
    if len(iterable) == 1 and isinstance(iterable[0], str):
        iterable = ([iterable[0]],)

    c = map(str, *iterable)
    return params.get('_default', None) if len(c) == 0 else ', '.join(c)


def get_ordered_list_of_strings(ordered_identifiers, list_to_order,
                        order_identifier_separator=',', case_sensitive=False):
    """
    functions sorts a list of string items according to sorted
    strings included in ordered_identifiers parameter;
    this function returns a new list object
    ordered_identifiers parameter could be a string of identifiers
    separated by separator or a list of identifiers
    """
    if ordered_identifiers == None or list_to_order == None \
        or len(ordered_identifiers) == 0 or len(list_to_order) == 0:
        return list_to_order
    list_ordered = []
    if isinstance(ordered_identifiers, list):
        ordered_names = ordered_identifiers
    else:
        ordered_names = get_as_list(
                    ordered_identifiers, separator=order_identifier_separator)
    for ordered_name in ordered_names:
        for name in list_to_order:
            if (case_sensitive is False
                    and name.lower() == ordered_name.lower()) \
                or (case_sensitive is True and name == ordered_name):
                list_ordered.append(name)
                break
    #append to the end items not founded in ordered_identifiers
    list_ordered[len(list_ordered):] = \
                [name for name in list_to_order if name not in list_ordered]
    if not len(list_ordered) == len(list_to_order):
        raise RuntimeError("size if ordered list doesn't equal source list")
    return list_ordered


def get_or_put(_dict, _key, _default):
    """
    function which puts a default value for a key if value is not occurs
    in dictionary
    """
    if not _dict == None:
        value = _dict.get(_key, None)
        if value == None:
            value = _default
            _dict[_key] = value
        return value


def is_empty(iterable):
    """
    function returns true if collection is None or has length equal 0
    """
    return iterable == None or len(iterable) == 0


def pop_from_list(_list, _value):
    """
    function pop an element from a list;
    it doesn't throw an exception if the element doesn't exist in the list
    """
    if not _list == None and _list.count(_value) > 0:
        _list.pop(_list.index(_value))


def remove_suffix(_collection, _suffix):
    """
    function removes suffix from all elements in collection
    """
    return [name[:-len(_suffix)] for name in
            [name for name in _collection if name.endswith(_suffix)]]


def get_as_string(_iterarable):
    pass
