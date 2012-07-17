from scipy import *
from pylab import *

def interpoluj(signal, annotation):
    #removing nonsinus beats from the beginning
    while annotation[0]!=0:
        signal=signal[1:-1]
        annotation=annotation[1:-1]
    #removing nonsinus beats from the end
    while annotation[-1]!=0:
        signal=signal[0:-2]
        annotation=annotation[0:-2]
    index_nonsin=find(annotation!=0)
    krok=1
    for i in arange(0, len(index_nonsin)):
        if i+1<=(len(index_nonsin)-1) and (index_nonsin[i+1]-index_nonsin[i])==1:
            krok+=1
        else:
            delta=(signal[index_nonsin[i]+1]-signal[index_nonsin[i]-krok])/(krok+1)
            for k in arange(1, krok+1):
                signal[index_nonsin[i]-krok+k]=signal[index_nonsin[i]-krok]+delta*k
            krok+=1
    return signal
