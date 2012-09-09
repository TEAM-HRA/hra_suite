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
    def __init__(self, signal, step):
        '''
        Constructor
        '''
        self.__signal__ = signal
        self.__step__ = step

    @property
    def sample(self):
        return self.__sample__(self.__signal__, self.__step__)

    def __sample__(self, signal, step):
        pass


class LinearInterpolatedSampling(Sampling):
    '''
    classdocs
    '''
    def __init__(self, signal, step=250):
        '''
        Constructor
        '''
        Sampling.__init__(self, signal, step)

    '''
    old def resample(signal, step=250):
    '''
    def __sample__(self, signal, step=250):
        """This function accepts two parameters. The first is the signal
        (signal intervals) which will be linearly interpolated, and the second
        is the step used for resampling. The result is the interpolated
        tachogram, sampled at the time interval given by the "step" value"""
        cum_signal = cumsum(signal)
        t_res = arange(0, sum(signal), step) * 0 + step
        #t_res[0]=0
        cum_t_res = cumsum(t_res)
        t_res = arange(0, sum(signal), step)
        t_res = t_res[0:-1]
        signal_res = []  # this is the variable which will contain
                    # the resampled tachogram
        i = 0
        k = 0
        for i in arange(0, len(signal) - 1):
            alpha = (signal[i + 1] - signal[i]) / signal[i + 1]
            while cum_t_res[k] < cum_signal[i + 1]:
                signal_res.append((cum_t_res[k] - cum_signal[i]) * alpha + signal[i]) #@IgnorePep8
                k += 1
            i += 1
        results = []
        results.append(t_res)
        results.append(signal_res)
        return results
