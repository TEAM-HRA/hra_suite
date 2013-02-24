'''
Created on 16-08-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.introspection import get_subclasses_short_names
    from pymath.sampling import LinearInterpolatedSampling
    from pymath.interpolation import InterpolationManager
    from pymath.integrals import DefiniteIntegral
    from pymath.utils.utils import get_values_as_map
except ImportError as error:
    print_import_error(__name__, error)


def get_fourier_transform(_fourier_transform_class_name):
    """
    returns fourier transform object based on _fourier_transform_class_name
    parameter
    """
    if _fourier_transform_class_name:
        try:
            return eval(_fourier_transform_class_name + '()')
        except NameError:
            print('Warning !!! Fourier transform ' + _fourier_transform_class_name + ' not defined !')  # @IgnorePep8
    return FourierTransformation()


class FourierTransformationManager(object):
    def __init__(self, _fourier_transform_name_or_class,
                 _interpolation_name_or_class=None):
        if isinstance(_fourier_transform_name_or_class, str):
            self.__fourier_transform__ = get_fourier_transform(
                                            _fourier_transform_name_or_class)
        elif not _fourier_transform_name_or_class == None:
            self.__fourier_transform__ = _fourier_transform_name_or_class()
        else:
            self.__fourier_transform__ = FourierTransformation()
        self.__interpolation_name_or_class__ = _interpolation_name_or_class

    def calculate(self, _data_vector, _excluded_annotations):
        if not self.__interpolation_name_or_class__ == None:
            interpolation = \
                InterpolationManager(self.__interpolation_name_or_class__)
            signal = interpolation.interpolate(_data_vector,
                                               _excluded_annotations)
        else:
            signal = _data_vector.signal

        return self.__fourier_transform__.calculate(signal)


class FourierTransformation(object):
    def calculate(self, _signal):
        return self.__calculate__(_signal)

    def __calculate__(self, _signal):
        return {}

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_short_names(FourierTransformation)


class FastFourierTransformation(FourierTransformation):
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
        boxcar = pl.array([1., 1., 1.0, 1.0]) * .25

        #resampling
        signal_resampled = LinearInterpolatedSampling(_signal, 250).sampling

        #filtering
        RR_resampled = pl.convolve(signal_resampled[1], boxcar)

        #preparing the resampled __signal__ for the fft routine
        t_resampled = signal_resampled[0]
        RR_resampled = RR_resampled - pl.mean(RR_resampled)

        results = FourierResults()

        #fast fourier transform calculation
        #moc = ((abs(fft(RR_resampled / len(RR_resampled - 1)))) ** 2) * 2
        results.moc = ((abs(pl.fft(RR_resampled
                                / len(RR_resampled - 1)))) ** 2) * 2

        #now we will calculate the frequencies
        # the total recording time is
        # the total time step

        time_total = t_resampled[-1] / 1000.0
        frequency = 1 / time_total
        freq = pl.arange(0, len(t_resampled)) * (frequency)
        results.frequency = pl.arange(0, len(t_resampled)) * (frequency)

        indexy = pl.find(freq < .5)

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
        variancja = pl.var(_signal)
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
