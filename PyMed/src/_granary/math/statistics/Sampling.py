'''
Created on 17-07-2012

@author: jurek
'''
from pylab import cumsum
from pylab import arange


class Sampling(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    @staticmethod
    def resample(signal, step=250):
        """This function accepts two parameters. The first is the signal
        (signal intervals) which will be linearly interpolated, and the second
        is the step used for resampling. The result is the interpolated
        tachogram, sampled at the time interval given by the "step" value"""
        cum_RR = cumsum(signal)
        t_res = arange(0, sum(signal), step) * 0 + step
        #t_res[0]=0
        cum_t_res = cumsum(t_res)
        t_res = arange(0, sum(signal), step)
        t_res = t_res[0:-1]
        RR_res = []  # this is the variable which will contain
                    # the resampled tachogram
        i = 0
        k = 0
        for i in arange(0, len(signal) - 1):
            alpha = (signal[i + 1] - signal[i]) / signal[i + 1]
            while cum_t_res[k] < cum_RR[i + 1]:
                RR_res.append((cum_t_res[k] - cum_RR[i]) * alpha + signal[i])
                k += 1
            i += 1
        results = []
        results.append(t_res)
        results.append(RR_res)
        return results
