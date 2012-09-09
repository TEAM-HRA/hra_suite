'''
Created on 17-07-2012

@author: jurek
'''

from pylab import sqrt
from pylab import size
from pylab import pi
from pylab import dot
from pylab import greater
from pylab import compress
from pylab import equal


def Mean(data):
    return sum(data) / float(size(data))


def SD(data):
    return sqrt(sum(((data - Mean(data)) ** 2)) / (size(data) - 1))


def SD1(data, shifted_data):
    return SD((data - shifted_data) / sqrt(2))


def SD2(data, shifted_data):
    return SD((data + shifted_data) / sqrt(2))


def SDRR(data):
    return SD(data)


def Ss(data, shifted_data):
    return pi * SD1(data, shifted_data) * SD2(data, shifted_data)


def SD21(data, shifted_data):
    return SD2(data, shifted_data) / SD1(data, shifted_data)


def R(data, shifted_data):
    x_pn = data - Mean(data)
    x_ppn = shifted_data - Mean(shifted_data)
    return dot(x_pn, x_ppn) / (sqrt(dot(x_pn, x_pn) * dot(x_ppn, x_ppn)))


def RMSSD(data, shifted_data):
    return sqrt(Mean((data - shifted_data) ** 2))


def SD1up(data, shifted_data):
    xrzut = (data - shifted_data) / sqrt(2)
    nad = compress(greater(0, xrzut), xrzut)
    return sqrt(sum(nad ** 2) / (size(xrzut) - 1))


def SD1down(data, shifted_data):
    xrzut = (data - shifted_data) / sqrt(2)
    pod = compress(greater(xrzut, 0), xrzut)
    return sqrt(sum(pod ** 2) / (size(xrzut) - 1))


def Nup(x_p, x_pp):
    xrzut = x_p - x_pp
    nad = compress(greater(0, xrzut), xrzut)
    return (size(nad))


def Ndown(x_p, x_pp):
    xrzut = x_p - x_pp
    pod = compress(greater(xrzut, 0), xrzut)
    return (size(pod))


def Non(x_p, x_pp):
    xrzut = x_p - x_pp
    na = compress(equal(xrzut, 0), xrzut)
    return (size(na))


def N_tot(x):
    return size(x) - 1
