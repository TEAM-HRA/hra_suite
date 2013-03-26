'''
Created on 04-02-2013

@author: jurek
'''
from pycore.introspection import get_subclasses

__UNITS_TYPE_MAP__ = {}


class __Unit__(object):
    def __init__(self, ordinal, name, label, lower_multiplier=1,
                 upper_multiplier=1):
        self.__ordinal__ = ordinal
        self.__name__ = name
        self.__label__ = label
        self.__lower_multiplier__ = lower_multiplier
        self.__upper_multiplier__ = upper_multiplier

    @property
    def ordinal(self):
        return self.__ordinal__

    @property
    def name(self):
        return self.__name__

    @property
    def label(self):
        return self.__label__

    @property
    def display_label(self):
        return '[%s]' % (self.name) if len(self.name) > 0  else ''

    @property
    def upper_multiplier(self):
        return self.__upper_multiplier__

    @property
    def lower_multiplier(self):
        return self.__lower_multiplier__

    def __gt__(self, other):
        if not self._type == other._type:
            raise TypeError('Incompatible types: ' + self + ' <=> ' + other)

    def expressInUnit(self, unit):
        value = 1.0
        if self.ordinal == unit.ordinal:
            pass
        elif self.ordinal < unit.ordinal:
            for _unit in get_units_for_type(self.get_unit_type()):
                if _unit.ordinal < self.ordinal:
                    continue
                elif _unit.ordinal >= unit.ordinal:
                    break
                value *= _unit.upper_multiplier
        elif self.ordinal > unit.ordinal:
            for _unit in get_units_for_type(self.get_unit_type()):
                if _unit.ordinal <= unit.ordinal:
                    continue
                elif _unit.ordinal > self.ordinal:
                    break
                value *= _unit.lower_multiplier
        return value

    def get_unit_type(self):
        pass


class __NoneUnit__(__Unit__):
    def __init__(self):
        super(__NoneUnit__, self).__init__(0, '', '')

NoneUnit = __NoneUnit__()


class __OrderUnit__(__Unit__):
    def __init__(self):
        super(__OrderUnit__, self).__init__(0, 'Order', '#')

OrderUnit = __OrderUnit__()


def __create_unit__(unit_type, unit_object):
    units = __UNITS_TYPE_MAP__.get(unit_type, [])
    units.append(unit_object)
    __UNITS_TYPE_MAP__[unit_type] = units
    return unit_object


class TimeUnit(__Unit__):
    """
    class which represents time unit
    """
    def get_unit_type(self):
        return TimeUnit


class __Millisecond__(TimeUnit):
    def __init__(self):
        super(__Millisecond__, self).__init__(-1, 'Millisecond', 'ms',
                                              upper_multiplier=1.0 / 1000)

Millisecond = __create_unit__(TimeUnit, __Millisecond__())


class __Second__(TimeUnit):
    def __init__(self):
        super(__Second__, self).__init__(0, 'Second', 's',
                            lower_multiplier=1000, upper_multiplier=1.0 / 60)

Second = __create_unit__(TimeUnit, __Second__())


class __Minute__(TimeUnit):
    def __init__(self):
        super(__Minute__, self).__init__(1, 'Minute', 'm',
                                lower_multiplier=60, upper_multiplier=1.0 / 60)

Minute = __create_unit__(TimeUnit, __Minute__())


class __Hour__(TimeUnit):
    def __init__(self):
        super(__Hour__, self).__init__(2, 'Hour', 'h', lower_multiplier=60)

Hour = __create_unit__(TimeUnit, __Hour__())


#sorting units according to ordinal numbers
for unit_type in __UNITS_TYPE_MAP__.keys():
    units = sorted(__UNITS_TYPE_MAP__.get(unit_type),
                   key=lambda unit: unit.ordinal)
    __UNITS_TYPE_MAP__[unit_type] = units


def get_units_for_type(_unit_type):
    return __UNITS_TYPE_MAP__.get(_unit_type)


def get_time_unit(label):
    for unit in __UNITS_TYPE_MAP__.get(TimeUnit):
        if unit.label == label:
            return unit


def get_unit_by_class_name(_class_name):
    """
    returns unit object based on unit class name
    """
    if _class_name:
        for subclass_unit in get_subclasses(__Unit__):
            if subclass_unit.__name__.endswith(_class_name):
                for unit_type in __UNITS_TYPE_MAP__:
                    for unit in __UNITS_TYPE_MAP__.get(unit_type):
                        if isinstance(unit, subclass_unit):
                            return unit
    return NoneUnit

if __name__ == '__main__':
    print('Hour.expressInUnit(Second): ' + str(Hour.expressInUnit(Second)))
    print('Second.expressInUnit(Hour): ' + str(Second.expressInUnit(Hour)))
    print('Hour.expressInUnit(Hour): ' + str(Hour.expressInUnit(Hour)))
    print('Hour.expressInUnit(Minute): ' + str(Hour.expressInUnit(Minute)))
    print('Minute.expressInUnit(Hour): ' + str(Minute.expressInUnit(Hour)))
    print('Millisecond.expressInUnit(Minute): ' + str(Millisecond.expressInUnit(Minute))) # @IgnorePep8
    print('Minute.expressInUnit(Millisecond): ' + str(Minute.expressInUnit(Millisecond))) # @IgnorePep8
    print("get_time_unit('m'): " + str(get_time_unit('m')))
