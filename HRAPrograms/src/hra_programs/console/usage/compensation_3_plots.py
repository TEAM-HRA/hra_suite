#!/usr/bin/env python
# coding: utf-8

'''
Created on Nov 26, 2013

@author: jurek
'''

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pylab
from matplotlib.font_manager import FontProperties

font_0 = FontProperties('DejaVu Sans')

# pylab.rc('text', usetex=True)
# pylab.rc('text.latex',unicode=True)
# pylab.rc('text.latex',preamble='\usepackage[T1]{polski}')
# pylab.rcParams['text.latex.preamble'] = [r'\boldmath']

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

font_1 = font_0.copy()
font_1.set_size('20')
font_1.set_weight('bold')

fig = plt.figure()
plt.title(u"Kompensacja asymetrii $\mathbf{C1_d}$, $\mathbf{C2_d}$ w 24-godzinnym nagraniu", fontproperties=font_1)

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
    leg = ax.legend(['$\mathbf{C1_d}$', '$\mathbf{C2_d}$'], loc='upper left')
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    ax.set_xlabel(u"Czas [godziny]", fontproperties=font_1)
    ax.set_ylabel(u"Wartość [%]", fontproperties=font_1)

plt.show()