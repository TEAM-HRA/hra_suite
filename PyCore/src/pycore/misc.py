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
