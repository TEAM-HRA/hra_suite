from pylab import *
from scipy import *

def filter(signal, annotation):
    indexy=find(annotation==0)
    indexy=array(indexy)
    signal=signal[indexy]
    return signal

def pfilter(signal, annotation):
    #wykrywanie i usuwanie nonsinus na poczatku i na koncu
    while annotation[0]!=0:
        signal=signal[1:-1]
        annotation=annotation[1:-1]
    #removing nonsinus beats from the end
    while annotation[-1]!=0:
        signal=signal[0:-2]
        annotation=annotation[0:-2]
    indexy_p=array(find(annotation!=0))
    indexy_m=indexy_p-1
    indexy=r_[indexy_p, indexy_m]
    x_p=signal[arange(0,len(signal)-1)]
    x_pp=signal[arange(1,len(signal))]
    x_p[indexy]=-1
    indexy=array(find(x_p!=-1))
    x_p=x_p[indexy]
    x_pp=x_pp[indexy]
    return x_p, x_pp
    
def Mean(x):
    return sum(x)/float(size(x))
    
def SD(x):
    return sqrt(sum(((x-Mean(x))**2))/(size(x)-1))

def SD1(x_p, x_pp):
    return SD((x_p-x_pp)/sqrt(2))

def SD2(x_p, x_pp):
    return SD((x_p+x_pp)/sqrt(2))

def SDRR(x):
    return SD(x)

def Ss(x_p, x_pp):
    return pi*SD1(x_p, x_pp)*SD2(x_p, x_pp)

def SD21(x_p, x_pp):
    return SD2(x_p,x_pp )/SD1(x_p, x_pp)

def R(x_p, x_pp):
    x_pn=x_p-Mean(x_p)
    x_ppn=x_pp-Mean(x_pp)
    return dot(x_pn, x_ppn)/(sqrt(dot(x_pn, x_pn)*dot(x_ppn, x_ppn)))
      
def RMSSD(x_p, x_pp):
    return sqrt(Mean((x_p-x_pp)**2))

def SD1up(x_p, x_pp):
    xrzut=(x_p-x_pp)/sqrt(2)
    nad=compress(greater(0,xrzut),xrzut)
    return sqrt(sum(nad**2)/(size(xrzut)-1))

def SD1down(x_p, x_pp):
    xrzut=(x_p-x_pp)/sqrt(2)
    pod=compress(greater(xrzut,0),xrzut)
    return sqrt(sum(pod**2)/(size(xrzut)-1))

def Nup(x_p, x_pp):
    xrzut=x_p-x_pp
    nad=compress(greater(0,xrzut),xrzut)
    return (size(nad))

def Ndown(x_p, x_pp):
    xrzut=x_p-x_pp
    pod=compress(greater(xrzut,0),xrzut)
    return (size(pod))

def Non(x_p, x_pp):
    xrzut=x_p-x_pp
    na=compress(equal(xrzut,0),xrzut)
    return (size(na))

def N_tot(x):
    return size(x)-1

def poincare(signal, annotation, filtering):
    if filtering==1:
        filtered_signal=filter(signal, annotation)
        x_p, x_pp=pfilter(signal,annotation)
    else:
        x_p=signal[arange(0,len(signal)-1)]
        x_pp=signal[arange(1,len(signal))]
        filtered_signal=signal
    
    RR_mean=Mean(filtered_signal)
    sdrr=SDRR(filtered_signal)
    rmssd=RMSSD(x_p, x_pp)
    sd1=SD1(x_p, x_pp)
    sd2=SD2(x_p, x_pp)
    sd21=SD21(x_p, x_pp)
    s=Ss(x_p, x_pp)
    r=R(x_p, x_pp)
    sd1up=SD1up(x_p, x_pp)
    sd1down=SD1down(x_p, x_pp)
    nup=Nup(x_p, x_pp)
    ndown=Ndown(x_p, x_pp)
    non=Non(x_p, x_pp)
    ntot=N_tot(filtered_signal)
    tot_time=sum(filtered_signal)/(1000*60)
    asym=0
    if sd1up>sd1down: asym=1
    return RR_mean, sdrr,rmssd,sd1,sd2,sd21,s,r,sd1up,sd1down,asym,nup,ndown,non,ntot,tot_time
