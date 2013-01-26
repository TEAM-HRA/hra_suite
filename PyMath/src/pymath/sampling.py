'''
Created on 17-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pylab import cumsum
    from pylab import arange
    from pylab import where
    from pylab import take
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
except ImportError as error:
    print_import_error(__name__, error)


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
    def sampling(self):
        return self.__sampling__(self.__signal__, self.__step__)

    def __sampling__(self, signal, step):
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
    def __sampling__(self, signal, step=250):

        if USE_NUMPY_EQUIVALENT:
            """ use more pythonic version of the method """
            return self.__numpy_sampling__(signal, step)

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

    def __numpy_sampling__(self, signal, step=250):
        """This function accepts two parameters. The first is the signal
        (signal intervals) which will be linearly interpolated, and the second
        is the step used for resampling. The result is the interpolated
        tachogram, sampled at the time interval given by the "step" value"""
        cum_signal = cumsum(signal)
        cum_res = cumsum(arange(0, sum(signal), step) * 0 + step)
        res = arange(0, sum(signal), step)[0:-1]
        signal_res = []  # this is the variable which will contain
                    # the resampled tachogram
        alphas = (signal[1:] - signal[:-1]) / signal[1:]
        for sig, cum_sig, cum_sig_next, alpha in \
                zip(signal[:-1], cum_signal[:-1], cum_signal[1:], alphas):
            idx = len(signal_res)
            signal_res[idx:] = \
                take(((cum_res[idx:] - cum_sig) * alpha + sig),
                     where(cum_res[idx:] < cum_sig_next))[0].tolist()
        return [res, signal_res]
