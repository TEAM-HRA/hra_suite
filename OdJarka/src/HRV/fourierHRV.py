from scipy import *
from re import *
from glob import *
from resample import *
from calka import *
from interpoluj import *

from imputuj import *

from matplotlib.mlab import *
from scipy.stats import *

def fourierHRV(signal, annotation, nonsin_out=1):
    """This function accepts three parameters. The first is the the name of the .rea file, the second is the column number for which the spectral analysis will be carried out, and the third is the step used for resampling. The result is a list containing (0) LF, HF, TP, (1) the power vector, (2) the frequencies"""
    
    #the file has been read and the signal in question is in list named "signal"

    #now the extra-sinus beats will be interpolated
    if nonsin_out == 1:
        signal=interpoluj(signal, annotation)

    #now (if the user so decides) the mean of the whole recording will be imputated in place of the nonsinus beats
    if nonsin_out ==2:
        signal=imputuj(signal, annotation)
    #the filter
    boxcar=array([1., 1., 1.0, 1.0])*.25

    #resampling
    signal_resampled=resample(signal,250)

    #filtering
    RR_resampled=convolve(signal_resampled[1], boxcar)

    #preparing the resampled signal for the fft routine
    t_resampled=signal_resampled[0]
    RR_resampled=RR_resampled-mean(RR_resampled)

    #fast fourier transform calculation
    moc=((abs(fft(RR_resampled/len(RR_resampled-1))))**2)*2

    #now we will calculate the frequencies
    # the total recording time is
    # the total time step

    time_total=t_resampled[-1]/1000.0
    frequency=1/time_total
    freq=arange(0, len(t_resampled))*(frequency)
    indexy=find(freq<.5)
    
    HF=calka(freq, moc,0.15, 0.4)
    LF=calka(freq,moc, 0.04, 0.15)
    TP=calka(freq, moc, 0,0.5) #we bear in mind, that we want to cut the negative frequencies and assign their variance to the positive frequencies
    TP0_4=calka(freq, moc, 0,0.4)
    VLF=calka(freq, moc, 0,0.04)
    LFHFTP=array([LF, HF, TP, TP0_4, VLF])
    rezultaty=[]
    rezultaty.append(LFHFTP)
    rezultaty.append(moc)
    rezultaty.append(freq)
    variancja=stats.var(signal) #just to be on the safe side
    return rezultaty
