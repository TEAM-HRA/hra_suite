'''
Created on 18-07-2012

@author: jurek
'''

from pylab import arange


from Filter import Filter
import _granary.math.statistics.DescriptiveStatistic as Statistics


class Poincare(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    @staticmethod
    def poincare(signal, annotation, filtering):
        if filtering == 1:
            filtered_signal = Filter.filter(signal, annotation)
            x_p, x_pp = Filter.pfilter(signal, annotation)
        else:
            x_p = signal[arange(0, len(signal) - 1)]
            x_pp = signal[arange(1, len(signal))]
            filtered_signal = signal

        RR_mean = Statistics.Mean(filtered_signal)
        sdrr = Statistics.SDRR(filtered_signal)
        rmssd = Statistics.RMSSD(x_p, x_pp)
        sd1 = Statistics.SD1(x_p, x_pp)
        sd2 = Statistics.SD2(x_p, x_pp)
        sd21 = Statistics.SD21(x_p, x_pp)
        s = Statistics.Ss(x_p, x_pp)
        r = Statistics.R(x_p, x_pp)
        sd1up = Statistics.SD1up(x_p, x_pp)
        sd1down = Statistics.SD1down(x_p, x_pp)
        nup = Statistics.Nup(x_p, x_pp)
        ndown = Statistics.Ndown(x_p, x_pp)
        non = Statistics.Non(x_p, x_pp)
        ntot = Statistics.N_tot(filtered_signal)
        tot_time = sum(filtered_signal) / (1000 * 60)
        asym = 0
        if sd1up > sd1down:
            asym = 1
        return (RR_mean, sdrr, rmssd, sd1, sd2, sd21, s, r, sd1up, sd1down,
                asym, nup, ndown, non, ntot, tot_time)
