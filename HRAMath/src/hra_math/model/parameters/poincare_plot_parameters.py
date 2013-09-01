'''
Created on 24 kwi 2013

@author: jurek
'''

from hra_math.utils.utils import print_import_error
try:
    from hra_core.collections_utils import nvl
    from hra_math.model.parameters.core_parameters import CoreParameters
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotParameters(CoreParameters):
    """
    very specific parameters concerning poincare plot
    """

    NAME = "poincare_plot_parameters"

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

    @property
    def progress_mark(self):
        """
        [optional]
        whether a progress mark have to be displayed during processing files
        default False
        """
        return self.__progress_mark__

    @progress_mark.setter
    def progress_mark(self, _progress_mark):
        self.__progress_mark__ = _progress_mark

    def setObjectPoincarePlotParameters(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'use_identity_line', self.use_identity_line)
        setattr(_object, 'use_buffer', self.use_buffer)
        setattr(_object, 'progress_mark', self.progress_mark)

    def validatePoincarePlotParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        pass

    def parameters_infoPoincarePlotParameters(self):
        print('Use buffer: ' + str(self.use_buffer))
        print('Use line of identity: ' + str(self.use_identity_line))
