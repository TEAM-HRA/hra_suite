'''
Created on 03-12-2012

@author: jurek
'''
from re import findall
from re import search


class Params(object):
    """
    class which represents dictionary parameters
    by object where elements are accessible with dot notation
    if client tries to access not existing element then None value is returned
    """
    def __init__(self, **params):
        for param in params:
            setattr(self, param, params[param])

    # if parameter is not set in the __init__() method then returns None
    def __getattr__(self, name):
        return None


def get_separator_between_numbers(_string):
    """
    function get a separator between numbers in a string;
    at first step the function fetches all non number elements from the string
    into a list, in the second step compares a string made by multiplication
    of the first element in the list by number of list elements with
    a string made by joining all elements of the list, if these two strings
    are equal then there is only one separator in the string
    """
    not_numbers = findall(r'[^0-9\.]+', _string)
    return not_numbers[0] \
        if len(not_numbers) > 0 and \
            not_numbers[0] * len(not_numbers) == "".join(not_numbers) \
        else None


def contains_letter(_string):
    return not search(r'[a-zA-Z]+', _string) == None


def is_empty(_value):
    if _value == None:
        return True
    elif hasattr(_value, '__len__'):
        return len(_value) == 0
    return False


def camel_format(_string):
    """
    a method which convert string in the form (an example):
    abcde_fghij_klmn
    into camel (format)
    abcdeFghijKlmn
    that means underline signs are removed and all first letter of words,
    except the first, (a word means a sequence between underlines) are upper
    case
    """
    if _string and len(_string.strip()) > 0:
        _string = _string.replace('_', ' ').title().replace(' ', '')
        return _string[0:1].lower() + _string[1:]
    return _string


def get_max_number_between_signs(iterable, left_sign='[', right_sign=']',
                                 from_end=False, default=None):
    """
    a method which return a maximum number (or None) between specified signs
    in elements of an iterable
    """
    max_num = None
    for item in iterable:
        item = str(item)
        if from_end == True:
            s_num = item[item.rfind(left_sign) + 1:item.rfind(right_sign)]
        else:
            s_num = item[item.find(left_sign) + 1:item.find(right_sign)]
        if len(s_num) > 0:
            try:
                num = int(s_num)
            except ValueError:
                continue
            if max_num == None:
                max_num = num
            if num > max_num:
                max_num = num
    return default if max_num == None else max_num


def replace_all(_string, replacement, matches):
    """
    function replaces all matches by replacement in the string _string
    """
    for match in matches:
        _string = _string.replace(match, replacement)
    return _string
