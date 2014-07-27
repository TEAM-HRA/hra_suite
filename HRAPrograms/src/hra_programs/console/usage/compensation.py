#!/usr/bin/env python
# coding: utf-8
'''
Created on Nov 26, 2013

@author: jurek
'''

import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pylab
from os.path import basename
import os.path as fs
import glob
from matplotlib.font_manager import FontProperties

# pylab.rc('text', usetex=True)
# pylab.rc('text.latex',unicode=True)
# pylab.rc('text.latex',preamble='\usepackage[T1]{polski}')
# pylab.rcParams['text.latex.preamble'] = [r'\boldmath']

#x = np.arange(10)

#matplotlib.use('GTK')


def bold_ticks_labels(plt, fontsize=11):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    plt.draw()
    axes = plt.axes()
    x_labels = [item.get_text() for item in axes.get_xaxis().get_ticklabels()]
    y_labels = [item.get_text() for item in axes.get_yaxis().get_ticklabels()]
    font_1 = font_0.copy()
    font_1.set_size(fontsize)
    font_1.set_weight('bold')

    axes.get_xaxis().set_ticklabels(x_labels, fontproperties=font_1)
    axes.get_yaxis().set_ticklabels(y_labels, fontproperties=font_1)

font_0 = FontProperties('DejaVu Sans')

file__ = '/home/jurek/volumes/doctoral/doktorat_przewod/dane/SVR_sliding__0001.res_out'
file__ = '/home/tmp/ANDRZ29_P/rr__small_24.rea_out'
file__ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out'
file__ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out'
file__ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
file__ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out'

file__ = '/home/tmp/jakubas_RR_P_timing/rr__jakubas_RR_P.rea_out'

save_fig = False
output_dir = "/home/tmp/timing_pngs/"
input_dir = None # "/home/tmp/long_corrected_5m_stepper_timing/"
input_extension = "*.rea_out"

if not fs.exists(output_dir):
    os.makedirs(output_dir)

if not input_dir == None:
    path = input_dir + input_extension
    files = [_file for _file in glob.glob(path)]
else:
    files = [file__]

usecols = (0, 1, 10)
usecols = (2, 3, 10)

#path = self.data_dir + nvl(self.extension, '*.*')
#return [_file for _file in glob.glob(path)]
for idx, file_ in enumerate(files):

    C1d, C2d, timing = np.loadtxt(file_,  usecols=usecols,
                           skiprows=1, delimiter=';', unpack=True) # @IgnorePep8
    #f = plt.figure()
    plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])

    #print('C1d: ' + str(C1d))
    #print('C2d: ' + str(C2d))
    #plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])

    #print(timing.dtype)
    #print('(0) timing: ' + str(timing))

    #timing = timing.astype(np.int32, copy=False)
    timing = timing / 3600000
    #print('timing: ' + str(timing))
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

    font_1 = font_0.copy()
    font_1.set_size('20')
    font_1.set_weight('bold')

    #plt.title(r'\huge{Kompensacja asymetrii $\mathbf{C1_a}$, $\mathbf{C2_a}$ w 24-godzinnym nagraniu EKG}')
    plt.title(u"Kompensacja asymetrii $\mathbf{C1_a}$, $\mathbf{C2_a}$ w 24-godzinnym nagraniu EKG", fontproperties=font_1)
    plt.plot(timing, C1d)
    plt.plot(timing, C2d)
    plt.axhline(0.5, lw=3)


    c1d_min = np.min(C1d)
    c1d_max = np.max(C1d)

    c2d_min = np.min(C2d)
    c2d_max = np.max(C2d)

    c_min = np.round(np.max([c1d_min, c2d_min]), decimals=1)
    c_max = np.round(np.max([c1d_max, c2d_max]), decimals=1)

    max_timing = np.max(timing)
    #print('max_timing: ' + str(max_timing))

    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,max_timing))
    plt.xticks(np.arange(0, int(max_timing)+1, 1))
    #plt.yticks(np.arange(c_min - 0.1, c_max + 0.1, 0.1))
    plt.yticks(np.arange(0, 1, 0.1))

    #usuniecie tickow
    #plt.xticks([])
    #plt.yticks([])

    plt.axes().set_xlim(0, max_timing)
    #plt.axes().set_ylim(c_min - 0.1, c_max + 0.1)
    plt.axes().set_ylim(0, 1)
    #
    ##plt.legend(['SD2w', 'SD2s'], loc='upper left')
    leg = plt.legend([u"$\mathbf{C1_a}$", u"$\mathbf{C2_a}$"], loc='upper left')
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    bold_ticks_labels(plt)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    plt.axes().set_xlabel(u"Czas [godziny]", fontproperties=font_1)
    plt.axes().set_ylabel(u"Wartość [%]", fontproperties=font_1)
    #

    png_file = output_dir + str(basename(file_)) + "_timing.png"
    if save_fig:
        plt.savefig(png_file) # save plot
        print('png file saved: ' + png_file)
        plt.cla()
    else:
        plt.show()  # show plot
