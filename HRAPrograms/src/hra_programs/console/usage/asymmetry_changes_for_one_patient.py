#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Created on Nov 26, 2013

@author: jurek
'''

#from __future__ import unicode_literals

import matplotlib
#matplotlib.use('GTK')
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import Image
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec

pl.rc('text', usetex=True)
pl.rc('text.latex',unicode=True)

preamble = [
            '\usepackage[polish]{babel}',
            #'\usepackage[utf8]{inputenc}',
            #'\usepackage[T1]{polski}'
            ]
#pylab.rc('text.latex',preamble=preamble)
pl.rc('text.latex',preamble='\usepackage[T1]{polski}') # oryg
#pylab.rc('text.latex',preamble='\usepackage[T1]{fontenc}')
#pylab.rc('text.latex',preamble='\usepackage{polski}')
pl.rcParams['text.latex.preamble'] = [r'\boldmath']


class Spec(object):

    def __init__(self, usecols, labels, file_, title=None, share_plot=True):
        self.usecols = usecols
        self.labels = labels
        self.file_ = file_
        self.title = title
        self.share_plot = share_plot


#x = np.arange(10)

#matplotlib.use('GTK')

#file_ = '/home/jurek/volumes/doctoral/doktorat_przewod/dane/SVR_sliding__0001.res_out'
#file_ = '/home/tmp/ANDRZ29_P/rr__small_24.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
#file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out'

#files = ['/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
#         ]


fig = plt.figure()

#adjustprops = dict(wspace=1)
#fig.subplots_adjust(**adjustprops)

#im = Image.open('/home/jurek/tmp/szeroki_tytul.png')
#height = im.size[1]
#im = np.array(im).astype(np.float) / 255
#fig.figimage(im, 0, fig.bbox.ymax - height, zorder=10)
#fig.figimage(im, 600, 930, zorder=10)


#plt.title(
#          r'\huge{Dynamika parametrów wariancyjnych HRV zwolnień i przyspieszeń rytmu serca w 24-godzinnym nagraniu}'
#          + '\n' + u'Do obliczeń wykorzystano przesuwające się 5-minutowe okno danych'
#
#          )
#plt.title(r'\huge{Dynamika parametrów wariancyjnych HRV zwolnień i przyspieszeń rytmu serca w 24-godzinnym nagraniu EKG ść}')

#plt.text(3.0, 0.6, r'żź do obliczeń wykorzystano przesuwające się 5-minutowe okno danych')
plt.xticks([])
plt.yticks([])

#0         ;  1         ;  2         ;  3         ;  4         ;  5         ;  6         ;  7         ;  8         ;  9         ;  10   g
#C1d       ;  C2d       ;  C1a       ;  C2a       ;  SD1d      ;  SD1a      ;  SD2d      ;  SD2a      ;  SDNNd     ;  SDNNa     ;  timing

file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/jakubas_RR_P.rea"

#rr = np.loadtxt(file_rr, usecols=(1,), skiprows=1, unpack=False ) #

file_ = "/home/tmp/jakubas_RR_P_timing/rr__jakubas_RR_P.rea_out"
specs = [
    Spec((8,9,10), ["SDNN_d", "SDNN_a"], file_),
    Spec((6,7,10), ["SD2_d", "SD2_a"], file_),
    Spec((4,5,10), ["SD1_d", "SD1_a"], file_),
    Spec((1,2,), ["RR"], file_rr, title="Tachogram", share_plot=True),
    ]

gs = gridspec.GridSpec(5, 1, height_ratios=[10,24,24,24,18])
#gs.update(left=0.03, right=0.98, hspace=0.15, wspace=0.9)
gs.update(left=0.04, right=0.99, wspace=0.1, hspace=0.2, bottom=0.04, top=0.97)

num_plot = (len(specs) + 1) * 100 + 10
num_plot = num_plot + 1
#ax_title = fig.add_subplot(num_plot)
ax_title = plt.subplot(gs[0])
#pyp = mpimg.imread('/home/jurek/tmp/tytul_hrv.png')
pyp = mpimg.imread('/home/jurek/volumes/doctoral/doktorat_wyniki/szeroki_tytul.png')
ax_title.imshow(pyp) #, origin='lower')
ax_title.set_axis_off()
ax_title.set_frame_on(False)
ax_title.autoscale_view('tight')

sharex = None

for idx, spec in enumerate(specs):
    des2 = None
    if len(spec.usecols) == 3:
        des1, des2, timing = np.loadtxt(spec.file_, usecols=spec.usecols,
                            skiprows=1, delimiter=';', unpack=True) # @IgnorePep8
    else:
        des1, annotation = np.loadtxt(spec.file_, usecols=spec.usecols,
                            skiprows=1, unpack=True)
        #odfiltrowanie adnotacji
        if (len(pl.array(pl.find(annotation != 0)) > 0)):
            des1 = des1[pl.array(pl.find(annotation == 0))]

        timing = np.cumsum(des1)
    timing = timing / 3600000

    num_plot = num_plot + 1
    if not sharex == None and spec.share_plot == True:
        #ax = fig.add_subplot(num_plot, sharex=sharex)
        ax = plt.subplot(gs[idx+1], sharex=sharex)
    else:
        #ax = fig.add_subplot(num_plot)
        ax = plt.subplot(gs[idx+1])
    sharex = ax
    if len(spec.labels) == 2:
        ax.set_color_cycle(['red', 'green'])
    else:
        ax.set_color_cycle(['blue'])

    des1_min = np.min(des1)
    des1_max = np.max(des1)

    des1_mean = np.mean(des1)
    if len(spec.labels) == 2:
        des2_mean = np.mean(des2)

    des1_count = None
    des2_count = None
    if len(spec.labels) == 2:
        des1_count = len(np.where(des1 > des2)[0])
        des2_count = len(np.where(des2 > des1)[0])

    if spec.title:
        #ax.text(len(timing)/2 - 100 , des1_max, spec.title, size=15)
        ax.text(np.mean(timing) , des1_max, spec.title, size=15)
        #ax.set_title(spec.title)

    ax.plot(timing, des1)
    if len(spec.labels) == 2:
        ax.plot(timing, des2)
        ax.axhline(des1_mean, lw=3, color='red')
        ax.axhline(des2_mean, lw=3, color='green')
    else:
        ax.axhline(des1_mean, lw=3, color='black')

    #ax.axhline(0.5, lw=3)

    if len(spec.labels) == 2:
        des2_min = np.min(des2)
        des2_max = np.max(des2)

        des_min = np.round(np.max([des1_min, des2_min]), decimals=1)
        des_max = np.round(np.max([des1_max, des2_max]), decimals=1)
    else:
        des_min = des1_min
        des_max = des1_max

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
    #ax.yaxis.set_ticks(np.arange(0, 1, 0.1))
    #ax.set_ylim(0, 1)
    #
    ##plt.legend(['SD2w', 'SD2s'], loc='upper left')
    if len(spec.labels) == 2:
        ax.legend(['$\mathbf{%s}$ Ilość $[%i]$ Średnia $[%i]$' % (spec.labels[0], des1_count, des1_mean),
                   '$\mathbf{%s}$ Ilość $[%i]$ Średnia $[%i]$' % (spec.labels[1], des2_count, des2_mean),
               #'Średnia $\mathbf{%s}$' % (spec.labels[0]), 'Średnia $\mathbf{%s}$' % (spec.labels[1])
               ],
              loc='upper left')
    else:
        ax.legend(['$\mathbf{%s}$' % (spec.labels[0]),
               #'Średnia $\mathbf{%s}$' % (spec.labels[0]), 'Średnia $\mathbf{%s}$' % (spec.labels[1])
               ],
              loc='upper left')
    if idx == 3:
        ax.set_xlabel(r'\Large{Czas [godziny]}')
    ax.set_ylabel(r'\Large{Wartość [ms]}')

#fig.text(
#        0.5, 0.05,
#        r'do obliczen wykorzystano 5-minutowe przesuwajace sie okno danych',
#        ha='left')
#plt.subplots_adjust(bottom=0.15)
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



