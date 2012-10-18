'''
Created on 16-08-2012

@author: jurek
'''

from pylab import convolve
from pylab import array
from pylab import fft
from pylab import arange
from pylab import mean
from pylab import find
import numpy as np

import pymath.interpolation as interpolation_module
from pymath.sampling import LinearInterpolatedSampling
from pymath.integrals import DefiniteIntegral
from pymath.datasources import DataSource
from pycore.collections import get_values_as_map
from pycore.collections import initialize_fields


class FourierTransform(DataSource):

    def __init__(self, data_source):
        '''
        Constructor
        '''
        DataSource.__init__(self, data_source)
        self.__interpolated_signal__ = None

    @property
    def calculate(self):

        if not self.__interpolated_signal__ == None:
            return self.__calculate__(self.__interpolated_signal__)
        else:
            return self.__calculate__(self.signal)

    def __calculate__(self, _signal):
        pass

    def __rrshift__(self, other):
        if (isinstance(other, DataSource)):
            DataSource.__init__(self, other)
            #self.__signal__ = other.__signal__
            return self.calculate()

    def __getattr__(self, name):
        # create interpolation object dynamically
        if name.startswith('interpolation_'):
            prefix_name = name[len('interpolation_'):].capitalize()
            if len(prefix_name) > 0:
                _class_name = prefix_name + 'Interpolation'
                interpolation_class = interpolation_module.__dict__.get(_class_name, None) #@IgnorePep8
                if interpolation_class:
                    interpolation_object = interpolation_class()
                    interpolation_object.signal = self.signal
                    interpolation_object.annotation = self.annotation
                    self.__interpolated_signal__ = interpolation_object.interpolate() #@IgnorePep8
                    return self
                else:
                    raise AttributeError('Unknown interpolation: ' + _class_name) #@IgnorePep8
        return name


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
        return results.values


## Class to hold outocomes of FastFourier calculations
class FourierResults(object):

    def __init__(self):
        initialize_fields(self, None)

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

    @property
    def values(self):
        return get_values_as_map(self, excluded_names=['values'])
