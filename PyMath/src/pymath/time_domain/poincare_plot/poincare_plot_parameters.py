'''
Created on 24 kwi 2013

@author: jurek
'''

from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import nvl
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotParameters(object):
    """
    very specific parameters concerning poincare plot
    """
    def __init__(self):
        self.__use_buffer__ = True

    @property
    def use_identity_line(self):
        """
        [optional]
        in calculation of sd1 use line of identity
        default: True
        """
        return nvl(self.__use_identity_line__, True)

    @use_identity_line.setter
    def use_identity_line(self, _use_identity_line):
        self.__use_identity_line__ = _use_identity_line

    @property
    def use_buffer(self):
        """
        [optional]
        in calculation of statistics use buffer
        default: True
        """
        return nvl(self.__use_buffer__, True)

    @use_buffer.setter
    def use_buffer(self, _use_buffer):
        self.__use_buffer__ = _use_buffer
