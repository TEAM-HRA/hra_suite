'''
Created on 02-03-2013

@author: jurek
'''
#to use print as a function not as a statement,
#it has to be the first statement in a module
from __future__ import print_function


class ProgressMark(object):
    """
    class used as counterpart of progress bar but for the console environment
    """
    def __init__(self, _label=None, _max_count=None):
        self.__mark_signs__ = ['|', '/', '-', '\\']
        self.__label__ = _label
        self.__max_count__ = abs(float(_max_count)) if _max_count else 0.0
        self.__counter__ = 0

    @property
    def reset(self):
        self.__counter__ = 0

    @property
    def tick(self):
        print('\r', end='')
        if self.__label__:
            print(self.__label__, end='')
        print(' [' + self.__mark_signs__[self.__counter__ % 4] + ']', end='')
        if self.__max_count__ == 0.0:
            percent = " [0]"
        else:
            percent = " [{0:6.2f} %]".format(((self.__counter__ / self.__max_count__) * 100)) # @IgnorePep8
        print(percent, end='')
        self.__counter__ = self.__counter__ + 1

    @property
    def label(self):
        return self.__label__

    @label.setter
    def label(self, _label):
        self.__label__ = _label

    @property
    def max_count(self):
        return self.__max_count__

    @max_count.setter
    def max_count(self, _max_count):
        self.__max_count__ = _max_count

    @property
    def close(self):
        """
        force of outcome of the next print statement in the next line
        """
        print('')
