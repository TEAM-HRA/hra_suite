'''
Created on 04-02-2013

@author: jurek
'''
from pycore.collections_utils import nvl

__UNITS_TYPE_MAP__ = {}


TIME_UNIT_TYPE = 'time'


class __Unit__(object):
    def __init__(self, name, ordinal, unit, unit_type, _id=None,
                 lower_multiplier=1, upper_multiplier=1):
        self.__name__ = name
        self.__ordinal__ = ordinal
        self.__unit__ = unit
        self.__unit_type__ = unit_type
        self.__id__ = nvl(_id, unit)
        self.__lower_multiplier__ = lower_multiplier
        self.__upper_multiplier__ = upper_multiplier
        units = __UNITS_TYPE_MAP__.get(unit_type, [])
        units.append(self)
        __UNITS_TYPE_MAP__[unit_type] = units

    @property
    def _id(self):
        return self.__id__

    @property
    def name(self):
        return self.__name__

    @property
    def ordinal(self):
        return self.__ordinal__

    @property
    def unit(self):
        return self.__unit__

    @property
    def unit_type(self):
        return self.__unit_type__

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
            for _unit in get_units_for_type(self.unit_type):
                if _unit.ordinal < self.ordinal:
                    continue
                elif _unit.ordinal >= unit.ordinal:
                    break
                value *= _unit.upper_multiplier
        elif self.ordinal > unit.ordinal:
            for _unit in get_units_for_type(self.unit_type):
                if _unit.ordinal <= unit.ordinal:
                    continue
                elif _unit.ordinal > self.ordinal:
                    break
                value *= _unit.lower_multiplier
        return value


class __Millisecond__(__Unit__):
    def __init__(self):
        super(__Millisecond__, self).__init__('Millisecond', -1, 'ms',
            TIME_UNIT_TYPE, _id='i', upper_multiplier=1.0 / 1000)

Millisecond = __Millisecond__()


class __Second__(__Unit__):
    def __init__(self):
        super(__Second__, self).__init__('Second', 0, 's',
             TIME_UNIT_TYPE, lower_multiplier=1000, upper_multiplier=1.0 / 60)

Second = __Second__()


class __Minute__(__Unit__):
    def __init__(self):
        super(__Minute__, self).__init__('Minute', 1, 'm',
            TIME_UNIT_TYPE, lower_multiplier=60, upper_multiplier=1.0 / 60)

Minute = __Minute__()


class __Hour__(__Unit__):
    def __init__(self):
        super(__Hour__, self).__init__('Hour', 2, 'h',
            TIME_UNIT_TYPE, lower_multiplier=60)

Hour = __Hour__()


#sorting units according to ordinal numbers
for unit_type in __UNITS_TYPE_MAP__.keys():
    units = sorted(__UNITS_TYPE_MAP__.get(unit_type),
                   key=lambda unit: unit.ordinal)
    __UNITS_TYPE_MAP__[unit_type] = units


def get_units_for_type(_unit_type):
    return __UNITS_TYPE_MAP__.get(_unit_type)


def get_time_unit(unit_name):
    for unit in __UNITS_TYPE_MAP__.get(TIME_UNIT_TYPE):
        if unit.unit == unit_name:
            return unit


if __name__ == '__main__':
    print(Hour.expressInUnit(Second))
    print(Second.expressInUnit(Hour))
    print(Hour.expressInUnit(Hour))
    print(Hour.expressInUnit(Minute))
    print(Minute.expressInUnit(Hour))
    print(Millisecond.expressInUnit(Minute))
    print(Minute.expressInUnit(Millisecond))
