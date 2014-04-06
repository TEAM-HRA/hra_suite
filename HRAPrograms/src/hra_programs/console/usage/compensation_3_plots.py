#encoding=utf-8
'''
Created on Nov 26, 2013

@author: jurek
'''

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pylab

pylab.rc('text', usetex=True)
pylab.rc('text.latex',unicode=True)
pylab.rc('text.latex',preamble='\usepackage[T1]{polski}')
pylab.rcParams['text.latex.preamble'] = [r'\boldmath']

#x = np.arange(10)

#matplotlib.use('GTK')

#file_ = '/home/jurek/volumes/doctoral/doktorat_przewod/dane/SVR_sliding__0001.res_out'
#file_ = '/home/tmp/ANDRZ29_P/rr__small_24.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out'

files = ['/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out',
         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out',
         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out',
         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
         ]

fig = plt.figure()
plt.title(r'\huge{Kompensacja asymetrii $\mathbf{C1_d}$, $\mathbf{C2_d}$ w 24-godzinnym nagraniu}')

plt.xticks([])
plt.yticks([])

num_plot = 410
for file_ in files:
    C1d, C2d, timing = np.loadtxt(file_,  # @IgnorePep8
                       skiprows=1, delimiter=';', unpack=True) # @IgnorePep8
    timing = timing / 3600000

    num_plot = num_plot + 1
    ax = fig.add_subplot(num_plot)
    ax.set_color_cycle(['red', 'green', 'blue', 'yellow'])

    ax.plot(timing, C1d)
    ax.plot(timing, C2d)
    ax.axhline(0.5, lw=3)

    c1d_min = np.min(C1d)
    c1d_max = np.max(C1d)

    c2d_min = np.min(C2d)
    c2d_max = np.max(C2d)

    c_min = np.round(np.max([c1d_min, c2d_min]), decimals=1)
    c_max = np.round(np.max([c1d_max, c2d_max]), decimals=1)

    max_timing = np.max(timing)
    #print('max_timing: ' + str(max_timing))

    ##plt.ticklabel_format(style='sci', axis='x', scilimits=(0,max_timing))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    #ax.xticks(np.arange(0, int(max_timing)+1, 1))
    ##plt.yticks(np.arange(c_min - 0.1, c_max + 0.1, 0.1))
    #ax.yticks(np.arange(0, 1, 0.1))
    ax.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax.set_xlim(0, max_timing)
    #plt.axes().set_ylim(c_min - 0.1, c_max + 0.1)
    ax.yaxis.set_ticks(np.arange(0, 1, 0.1))
    ax.set_ylim(0, 1)
    #
    ##plt.legend(['SD2w', 'SD2s'], loc='upper left')
    ax.legend(['$\mathbf{C1_d}$', '$\mathbf{C2_d}$'], loc='upper left')
    ax.set_xlabel(r'\Large{Czas [godziny]}')
    ax.set_ylabel(r'\Large{Wartość}')

plt.show()



#plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])

#print(timing.dtype)

#timing = timing.astype(np.int32, copy=False)
#print(timing)
#plt.plot(x, x)
#plt.plot(x, 2 * x)
#plt.plot(x, 3 * x)
#plt.plot(x, 4 * x)

#plt.legend(['y = x', 'y = 2x', 'y = 3x', 'y = 4x'], loc='upper left')


#plt.plot(SD2w)
#plt.plot(SD2s)

#fig = plt.figure()
#x = np.arange(55)
#ax1 = fig.add_subplot(311)
#ax1.plot(x, x)
#ax2 = fig.add_subplot(312, sharex=ax1)
#ax2.plot(2 * x, 2 * x)
#ax3 = fig.add_subplot(313, sharex=ax1)
#ax3.plot(3 * x, 3 * x)
#plt.show()


#plt.title(r'\huge{Kompensacja asymetrii $\mathbf{C1_d}$, $\mathbf{C2_d}$ w 24-godzinnym nagraniu}')
#plt.plot(timing, C1d)
#plt.plot(timing, C2d)
#plt.axhline(0.5, lw=3)
#
#c1d_min = np.min(C1d)
#c1d_max = np.max(C1d)
#
#c2d_min = np.min(C2d)
#c2d_max = np.max(C2d)
#
#c_min = np.round(np.max([c1d_min, c2d_min]), decimals=1)
#c_max = np.round(np.max([c1d_max, c2d_max]), decimals=1)
#
#
#max_timing = np.max(timing)
##print('max_timing: ' + str(max_timing))
#
#
##plt.ticklabel_format(style='sci', axis='x', scilimits=(0,max_timing))
#plt.xticks(np.arange(0, int(max_timing)+1, 1))
##plt.yticks(np.arange(c_min - 0.1, c_max + 0.1, 0.1))
#plt.yticks(np.arange(0, 1, 0.1))
#
#plt.axes().set_xlim(0, max_timing)
##plt.axes().set_ylim(c_min - 0.1, c_max + 0.1)
#plt.axes().set_ylim(0, 1)
##
###plt.legend(['SD2w', 'SD2s'], loc='upper left')
#plt.legend(['$\mathbf{C1_d}$', '$\mathbf{C2_d}$'], loc='upper left')
#plt.axes().set_xlabel(r'\Large{Czas [godziny]}')
#plt.axes().set_ylabel(r'\Large{Wartość}')
##
#plt.show()  # show plot
##plt.savefig("/home/tmp/my_fig.png") # save plot
