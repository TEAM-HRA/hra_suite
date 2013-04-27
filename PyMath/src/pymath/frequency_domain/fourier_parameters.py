'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import commas
    from pymath.model.core_parameters import CoreParameters
    from pymath.frequency_domain.fourier import FourierTransformation
    from pymath.interpolation import Interpolation
except ImportError as error:
    print_import_error(__name__, error)


def getFourierTransformationNames():
    """
    to get default fourier transformation names; subclasses of
    FourierTransformation class
    """
    return commas(FourierTransformation.getSubclassesShortNames())


def getInterpolationNames():
    """
    to get default interpolations names; subclasses of Interpolation class
    """
    return commas(Interpolation.getSubclassesShortNames())


class FourierParameters(CoreParameters):
    """
    parameters concerning fourier transformation
    """
    NAME = "fourier_parameters"

    def __init__(self):
        pass

    @property
    def fourier_transformation(self):
        """
        [optional]
        use fourier transformation
        to get list of fourier transformations call a function:
        getFourierTransformationNames()
        [module: pymath.time_domain.poincare_plot.poincare_plot]
        """
        return self.__fourier_transformation__

    @fourier_transformation.setter
    def fourier_transformation(self, _fourier_transformation):
        self.__fourier_transformation__ = _fourier_transformation

    @property
    def fourier_transform_interpolation(self):
        """
        [optional]
        use interpolation method during fourier transformation
        to get list of fourier transformations interpolations call a function:
        getInterpolationNames()
        [module: pymath.time_domain.poincare_plot.poincare_plot]
        """
        return self.__fourier_transform_interpolation__

    @fourier_transform_interpolation.setter
    def fourier_transform_interpolation(self, _fourier_transform_interpolation):  # @IgnorePep8
        self.__fourier_transform_interpolation__ = \
                _fourier_transform_interpolation

    def setFourierProperties(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'fourier_transformation', self.fourier_transformation)
        setattr(_object, 'fourier_transform_interpolation', self.fourier_transform_interpolation) # @IgnorePep8

    def validateFourierParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        pass
