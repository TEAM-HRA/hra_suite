'''
Created on 17-07-2012

@author: jurek
'''

from pylab import convolve
from pylab import array
from pylab import find
from pylab import fft
from pylab import arange
from pylab import mean
import numpy as np

from _granary.math.interpolation.Interpolation import Interpolation
from _granary.math.integrals.DefiniteIntegral import DefiniteIntegral
from _granary.math.statistics.Sampling import Sampling
from _granary.math.imputuj import imputuj


class Fourier(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    @staticmethod
    def fourierHRV(signal, annotation, nonsin_out=1):
        """This function accepts three parameters. The first is the the name of
         the .rea file, the second is the column number for which the spectral
         analysis will be carried out, and the third is the step used for
         resampling. The result is a list containing (0) LF, HF, TP,
         (1) the power vector, (2) the frequencies"""

        #the file has been read and the signal in question is
        #in list named "signal"

        #now the extra-sinus beats will be interpolated
        if nonsin_out == 1:
            signal = Interpolation.interpoluj(signal, annotation)

        #now (if the user so decides) the mean of the whole recording will
        #be imputated in place of the nonsinus beats
        if nonsin_out == 2:
            signal = imputuj(signal, annotation)
        #the filter
        boxcar = array([1., 1., 1.0, 1.0]) * .25

        #resampling
        signal_resampled = Sampling.resample(signal, 250)

        #filtering
        RR_resampled = convolve(signal_resampled[1], boxcar)

        #preparing the resampled signal for the fft routine
        t_resampled = signal_resampled[0]
        RR_resampled = RR_resampled - mean(RR_resampled)

        #fast fourier transform calculation
        moc = ((abs(fft(RR_resampled / len(RR_resampled - 1)))) ** 2) * 2

        #now we will calculate the frequencies
        # the total recording time is
        # the total time step

        time_total = t_resampled[-1] / 1000.0
        frequency = 1 / time_total
        freq = arange(0, len(t_resampled)) * (frequency)
        indexy = find(freq < .5)

        HF = DefiniteIntegral.integration(freq, moc, 0.15, 0.4)
        LF = DefiniteIntegral.integration(freq, moc, 0.04, 0.15)

        #we bear in mind, that we want to cut the negative frequencies
        #and assign their variance to the positive frequencies
        TP = DefiniteIntegral.integration(freq, moc, 0, 0.5)

        TP0_4 = DefiniteIntegral.integration(freq, moc, 0, 0.4)
        VLF = DefiniteIntegral.integration(freq, moc, 0, 0.04)
        LFHFTP = array([LF, HF, TP, TP0_4, VLF])
        rezultaty = []
        rezultaty.append(LFHFTP)
        rezultaty.append(moc)
        rezultaty.append(freq)
        #just to be on the safe side
        variancja = np.var(signal)
        return rezultaty
