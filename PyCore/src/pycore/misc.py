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


def is_empty(_string):
    return True if _string == None or len(_string) == 0 else False


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
