'''
Created on 16-08-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import numpy as np
    from pylab import convolve
    from pylab import array
    from pylab import fft
    from pylab import arange
    from pylab import mean
    from pylab import find
    import pymath.interpolation as interpolation_module
    from pymath.sampling import LinearInterpolatedSampling
    from pymath.integrals import DefiniteIntegral
    from pymath.datasources import DataVector
    from pymath.utils.utils import get_values_as_map
except ImportError as error:
    print_import_error(__name__, error)


class FourierTransformManager(object):
    def __init__(self, _fourier_transform_class, _interpolation_type=None):
        self.__fourier_transform_class__ = _fourier_transform_class
        self.__interpolation_type__ = _interpolation_type

    def calculate(self, _data):
        fourier_transform = self.__fourier_transform_class__(_data)
        if len(self.__interpolation_type__) > 0:
            signal = self.__get_interpolated_value__(_data)
            fourier_transform.data = DataVector(signal=signal)
        return fourier_transform.calculate()

    def __get_interpolated_value__(self, _data):
        _class_name = self.__interpolation_type__ + 'Interpolation'
        interpolation_class = interpolation_module.__dict__.get(_class_name, None) #@IgnorePep8
        if interpolation_class:
            interpolation_object = interpolation_class()
            interpolation_object.signal = _data.signal
            interpolation_object.annotation = _data.annotation
            return interpolation_object.interpolate()
        raise AttributeError('Unknown interpolation: ' + _class_name)


class FourierTransform(DataVector):
    def __init__(self, data_source):
        '''
        Constructor
        '''
        DataVector.__init__(self, data_source)

    def calculate(self):
        return self.__calculate__(self.signal)

    def __calculate__(self, _signal):
        pass


class FastFourierTransform(FourierTransform):
    def __init__(self, data_source):
        '''
        Constructor
        '''
        FourierTransform.__init__(self, data_source)

    def __calculate__(self, _signal):
        """This function accepts three results. The first is the the name of
         the .rea file, the second is the column number for which the spectral
         analysis will be carried out, and the third is the step used for
         resampling. The result is a list containing (0) LF, HF, TP,
         (1) the power vector, (2) the frequencies"""

        #the file has been read and the __signal__ in question is
        #in list named "__signal__"

        # signal could be already interpolated if
        # interpolation_<name> property is called before calculate method
        #now the extra-sinus beats will be interpolated
        #if nonsin_out == 1:
        #    _signal = Interpolation.interpoluj(_signal, annotation)

        # signal could be already interpolated if
        # interpolation_<name> property is called before calculate method
        #now (if the user so decides) the mean of the whole recording will
        #be imputated in place of the nonsinus beats
        # code moved to
        # med.time_domain.poincare_plot.filters.MeanAnnotationFilter
        #if nonsin_out == 2:
        #    __signal__ = imputuj(__signal__, annotation)
        #the filter
        boxcar = array([1., 1., 1.0, 1.0]) * .25

        #resampling
        signal_resampled = LinearInterpolatedSampling(_signal, 250).sampling

        #filtering
        RR_resampled = convolve(signal_resampled[1], boxcar)

        #preparing the resampled __signal__ for the fft routine
        t_resampled = signal_resampled[0]
        RR_resampled = RR_resampled - mean(RR_resampled)

        results = FourierResults()

        #fast fourier transform calculation
        #moc = ((abs(fft(RR_resampled / len(RR_resampled - 1)))) ** 2) * 2
        results.moc = ((abs(fft(RR_resampled
                                / len(RR_resampled - 1)))) ** 2) * 2

        #now we will calculate the frequencies
        # the total recording time is
        # the total time step

        time_total = t_resampled[-1] / 1000.0
        frequency = 1 / time_total
        freq = arange(0, len(t_resampled)) * (frequency)
        results.frequency = arange(0, len(t_resampled)) * (frequency)

        indexy = find(freq < .5)

        results.HF = DefiniteIntegral.integration(results.frequency, results.moc, 0.15, 0.4) #@IgnorePep8
        results.LF = DefiniteIntegral.integration(results.frequency, results.moc, 0.04, 0.15) #@IgnorePep8

        #we bear in mind, that we want to cut the negative frequencies
        #and assign their variance to the positive frequencies
        results.TP = DefiniteIntegral.integration(results.frequency, results.moc, 0, 0.5) #@IgnorePep8
        results.TP0_4 = DefiniteIntegral.integration(results.frequency, results.moc, 0, 0.4) #@IgnorePep8
        results.VLF = DefiniteIntegral.integration(results.frequency, results.moc, 0, 0.04) #@IgnorePep8
        #LFHFTP = array([LF, HF, TP, TP0_4, VLF])

        #rezultaty = []
        #rezultaty.append(LFHFTP)
        #rezultaty.append(moc)
        #rezultaty.append(freq)
        #just to be on the safe side
        variancja = np.var(_signal)
        #return rezultaty
        return get_values_as_map(results)


## Class to hold outocomes of FastFourier calculations
class FourierResults(object):

    @property
    def HF(self):
        return self.__HF__

    @HF.setter
    def HF(self, HF):
        self.__HF__ = HF

    @property
    def LF(self):
        return self.__LF__

    @LF.setter
    def LF(self, LF):
        self.__LF__ = LF

    @property
    def TP(self):
        return self.__TP__

    @TP.setter
    def TP(self, TP):
        self.__TP__ = TP

    @property
    def TP0_4(self):
        return self.__TP0_4__

    @property
    def TP0_5(self):
        return self.TP0_4

    @TP0_4.setter
    def TP0_4(self, TP0_4):
        self.__TP0_4__ = TP0_4

    ## Method which returns VLF value
    #  @return VLF value
    @property
    def VLF(self):
        return self.__VLF__

    ## Method to set up VLF value
    @VLF.setter
    def VLF(self, VLF):
        self.__VLF__ = VLF

    @property
    def frequency(self):
        return self.__frequency__

    @frequency.setter
    def frequency(self, frequency):
        self.__frequency__ = frequency

    @property
    def moc(self):
        return self.__moc__

    @moc.setter
    def moc(self, moc):
        self.__moc__ = moc

    @property
    def LFnu(self):
        return (self.LF / (self.TP0_4 - self.VLF)) * 100

    @property
    def HFnu(self):
        return (self.HF / (self.TP0_4 - self.VLF)) * 100

    # if parameter is not set then returns None
    def __getattr__(self, name):
        return None
