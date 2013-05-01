'''
Created on 03-12-2012

@author: jurek
'''
from re import findall
from re import search
import collections


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


def get_separator_between_numbers(_string, _default=' '):
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
        else _default


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


def fixed_size_string(_string, size):
    return ('{:' + str(size) + 's}').format(_string) if len(_string) < size \
            else _string[:size]


def extract_number(_string, convert=None):
    try:
        return int(_string)
    except ValueError:
        pass
    _string = _string.strip()
    _number = filter(lambda x: x.isdigit(), _string)
    if is_empty(_number):
        return None
    return _number if convert == None else convert(_number)


def extract_alphabetic(_string, strip=True, convert=None):
    if not hasattr(_string, 'strip'):  # this means some numeric value
        return None
    if strip:
        _string = _string.strip()
    _string = filter(lambda x: not x.isdigit(), _string)
    if strip == True and is_empty(_string):
        return None
    return _string if convert == None else convert(_string)


SeparatorItem = collections.namedtuple("SeparatorItem", "sign id_ label")


class __SeparatorSpec__(SeparatorItem):

    COUNTER = 0

    def __init__(self, sign, id_, _label):
        __SeparatorSpec__.COUNTER = __SeparatorSpec__.COUNTER + 1
        self.counter = __SeparatorSpec__.COUNTER

    @property
    def counter(self):
        return self.__counter__

    @counter.setter
    def counter(self, _counter):
        self.__counter__ = _counter


class Separator(object):
    NONE = __SeparatorSpec__('', '', '')
    #actually this means any white space not only a usual space
    WHITE_SPACE = __SeparatorSpec__(' ', 'separator.white.space', 'White space')  # @IgnorePep8
    SEMICOLON = __SeparatorSpec__(';', 'separator.semicolon', 'Semicolon')
    DASH = __SeparatorSpec__('-', 'separator.dash', 'Dash')
    COMMA = __SeparatorSpec__(',', 'separator.comma', 'Comma')
    CUSTOM = __SeparatorSpec__(-1, 'separator.custom', 'Custom')

    __SEPARATORS__ = None

    @staticmethod
    def getSeparators():
        if not Separator.__SEPARATORS__:
            Separator.__SEPARATORS__ = [getattr(Separator, name)
                for name in dir(Separator)
                if not name.startswith('get') and not name.startswith('__')]
        return Separator.__SEPARATORS__

    @staticmethod
    def getSeparatorsSpec(label_handler=None):
        separators_specs = []
        for member in dir(Separator):
            separator = getattr(Separator, member)
            if isinstance(separator, __SeparatorSpec__):
                if not separator == Separator.NONE:
                    if label_handler:
                        separator_spec = __SeparatorSpec__(separator.sign,
                                    separator.id_, label_handler(separator))
                        separator_spec.counter = separator.counter
                        separators_specs.append(separator_spec)
                    else:
                        separators_specs.append(separator)
        return sorted(separators_specs, key=lambda separator: separator.sign)

    @staticmethod
    def getSeparatorsLabels(label_handler=None):
        return [separator_spec.label for separator_spec
                    in Separator.getSeparatorsSpec(label_handler)
                        if not separator_spec == Separator.CUSTOM]

    @staticmethod
    def getSeparatorSign(sign):
        if not sign == None and len(sign.strip()) == 0:
            return Separator.WHITE_SPACE
        for member in dir(Separator):
            separator = getattr(Separator, member)
            if isinstance(separator, __SeparatorSpec__) \
                and separator.sign == sign:
                return separator
        return Separator.CUSTOM if not sign == None else Separator.NONE


def format_decimal(value, precision):
    """
    function formatting decimal value according to passed precision
    """
    if isinstance(precision, tuple):
        return "%{prec}.{scale}f".format(prec=precision[0],
                                scale=precision[1]) % value
    else:
        return value


def raw_string(_str):
    """
    get string in a raw format
    """
    return "%r" % _str
