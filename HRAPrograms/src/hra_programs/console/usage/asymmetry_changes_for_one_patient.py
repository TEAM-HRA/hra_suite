#!/usr/bin/env python
# coding: utf-8

'''
Created on Nov 26, 2013

@author: jurek
'''

# from __future__ import unicode_literals

import os
import os.path as fs
import matplotlib
# matplotlib.use('GTK')
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import Image
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import glob


font_0 = FontProperties('DejaVu Sans')

# 1
#pl.rc('text', usetex=True)
#pl.rc('text.latex', unicode=True)

save_plot = True
#figsize = (30.0, 15.0)
figsize = (18, 21)

# 1
# preamble = [
#             '\usepackage[polish]{babel}',
#             # '\usepackage[utf8]{inputenc}',
#             # '\usepackage[T1]{polski}'
#             ]
# pylab.rc('text.latex',preamble=preamble)
# 1
# pl.rc('text.latex', preamble='\usepackage[T1]{polski}')  # oryg
# pylab.rc('text.latex',preamble='\usepackage[T1]{fontenc}')
# pylab.rc('text.latex',preamble='\usepackage{polski}')
# 1
# pl.rcParams['text.latex.preamble'] = [r'\boldmath']


def get_first_lines(_file, count=1):
    """
    get first count lines of a text file
    """
    return [line for idx, line in enumerate(open(_file)) if idx < count]


def bold_ticks_labels(ax, fontsize=11):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    fig.canvas.draw()

    x_labels = [item.get_text() for item in ax.get_xticklabels()]
    y_labels = [item.get_text() for item in ax.get_yticklabels()]

    font_1 = font_0.copy()
    font_1.set_size(fontsize)
    font_1.set_weight('bold')

    ax.set_xticklabels(x_labels, fontproperties=font_1)
    ax.set_yticklabels(y_labels, fontproperties=font_1)


def bold_legend(leg):
    #change legend font properties
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')


class Spec(object):

    def __init__(self, usecols, labels, file_, title=None, share_plot=True,
                 plot_type='-', annotation=False, value=None,
                 time_label=False, numpoints=2, mean_line=False,
                 y_label=u"Wartość [ms]", percentage=False):
        self.usecols = usecols
        self.labels = labels
        self.file_ = file_
        self.title = title
        self.share_plot = share_plot
        self.plot_type = plot_type
        self.annotation = annotation
        self.value = value
        self.time_label = time_label
        self.numpoints = numpoints
        self.mean_line = mean_line
        self.y_label = y_label
        self.percentage = percentage


class Sources(object):

    def __init__(self, file_, file_rr):
        self.file_ = file_
        self.file_rr = file_rr


# file_ = '/home/jurek/volumes/doctoral/doktorat_przewod/dane/SVR_sliding__0001.res_out'
# file_ = '/home/tmp/ANDRZ29_P/rr__small_24.rea_out'
# file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out'
# file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out'
# file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
# file_ = '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out'

# files = ['/home/jurek/volumes/doctoral/doktorat_wyniki/rr__struzik_RR_P_MIN_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__sprzacz_RR_P_MEDIUM_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__PRECZ05_P_MEDIUM_2_ASYMMETRY.rea_out',
#         '/home/jurek/volumes/doctoral/doktorat_wyniki/rr__NIEZ40_P_MAX_ASYMMETRY.rea_out'
#         ]

def create_ax_title(gs):
    # empty plot
    title_plot = plt.subplot(gs[0])
    title_plot.grid(False)
    title_plot.set_frame_on(False)
    title_plot.title.set_visible(False)
    title_plot.xaxis.set_major_locator(plt.NullLocator())
    title_plot.yaxis.set_major_locator(plt.NullLocator())
    for tl in title_plot.get_xticklabels():
        tl.set_visible(False)
    for tl in title_plot.get_yticklabels():
        tl.set_visible(False)

    alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}

    text_fontsize = 20
    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')

    text = u"Dynamika parametrów wariancyjnych HRV zwolnień i przyspieszeń rytmu serca w 24-godzinnym nagraniu"
    text_color = "black"
    title_plot.text(0.5, 0.7, text,
            #fontsize=text_fontsize,
            color=text_color,
            fontproperties=font_1,
            **alignment)

    text_fontsize = 15
    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')
    if skokowo:
        text = u"[Do obliczeń parametrów wariancyjnych użyto 5-minutowe sąsiadujące okna danych]"
    else:
        text = u"[Do obliczeń wykorzystano przesuwające się 5-minutowe okno danych]"
    title_plot.text(0.5, 0.25, text,
                #fontsize=text_fontsize,
                color=text_color,
                fontproperties=font_1,
                **alignment)


fig = plt.figure(figsize=figsize)


plt.xticks([])
plt.yticks([])

# 0         ;  1         ;  2         ;  3         ;  4         ;  5         ;  6         ;  7         ;  8         ;  9         ;  10   g
# C1d       ;  C2d       ;  C1a       ;  C2a       ;  SD1d      ;  SD1a      ;  SD2d      ;  SD2a      ;  SDNNd     ;  SDNNa     ;  timing

file_rr = "/home/jurek/volumes/doctoral/dane/24h_shuffled/part1/S_jakubas_RR.rea"  # dane potasowane
file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/kolter_RR_P.rea"
# file_rr = "/tmp/kolter_RR_P/Skolter_RR_P.rea"
# rr = np.loadtxt(file_rr, usecols=(1,), skiprows=1, unpack=False ) #
file_rr = "/tmp/kolter_RR_P/S_kolter_RR_P.rea"
file_rr = "/tmp/kolter_RR_P_5/S_kolter_RR_P.rea"
file_rr = "/home/tmp/outcomes_4/S_jakubas_RR_P_1_32.rea"
file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/bucior_RR_P.rea"
file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/jakubas_RR_P.rea"

file_ = "/tmp/tmp17/rr__S_jakubas_RR.rea_out"  # dane potasowane
file_ = '/tmp/bucior_RR_P/rr__bucior_RR_P.rea_out'
file_ = '/tmp/kolter_RR_P/rr__kolter_RR_P.rea_out'
file_ = '/tmp/kolter_RR_P/s_rr__Skolter_RR_P.rea_out'
file_ = '/tmp/kolter_RR_P_3/S_rr__kolter_RR_P.rea_out'
file_ = '/tmp/kolter_RR_P_5/S_rr__S_kolter_RR_P.rea_out'
file_ = '/tmp/kolter_RR_P/rr__S_kolter_RR_P.rea_out'
file_ = '/home/tmp/outcomes_4/rr__S_jakubas_RR_P_1_32.rea_out'
file_ = '/tmp/bucior_RR_P/rr__bucior_RR_P.rea_out'
file_ = "/home/tmp/jakubas_RR_P_timing/rr__jakubas_RR_P.rea_out"
file_ = "/home/tmp/jakubas_RR_P_timing/rr_skokowo_jakubas_RR_P.rea_out"
file_ = "/x/tmp/jakubas_RR_P_timing/rr_skokowo_jakubas_RR_P.rea_out"
skokowo = True


sources = [Sources(file_, file_rr)]

# sources = []
# files_rr = glob.glob('/home/tmp/24_h_5m_stepper/*.rea')
# for file_rr in files_rr:
#    path = fs.dirname(file_rr)
#    filename = "rr__" + os.path.basename(file_rr) + '_out'
#    file_ = fs.normpath(fs.join(path, filename))
#    sources.append(Sources(file_, file_rr))

def get_idx(_list, value):
    value = value.lower()
    return _list.index(value) if _list.count(value) == 1 else -1


def generate_asymmetry_changes(file_, file_rr):
    if save_plot:
        print('Processing file: ' + str(file_rr))

    lines = get_first_lines(file_, 1)
    headers = [header.lower().strip() for header in lines[0].split(';')] if len(lines) > 0 else []  # @IgnorePep8
    t_idx = get_idx(headers, 'timing')

    specs = [
        #Spec((get_idx(headers, 'C1d'), t_idx), ["C1_d"], file_, value=0.5),#, plot_type='o'),
        #Spec((get_idx(headers, 'C2a'), t_idx), ["C2_a"], file_, value=0.5),#, plot_type='o'),
        #Spec((get_idx(headers, 'C2a'), t_idx), ["Ca"], file_, value=0.5),#, plot_type='o'),
        # Spec((0,3,10), ["C1_d", "C2_a"], file_, plot_type='o'),
        Spec((1, 2,), ["RR"], file_rr, title="Tachogram", #share_plot=True,
             annotation=True, y_label=u"RR [ms]"), #, time_label=True),
        Spec((get_idx(headers, 'sd1d'), get_idx(headers, 'sd1a'), t_idx),
             ["SD1_d", "SD1_a"], file_, title=u"(A) Zmienność krótkoterminowa",
             share_plot=False, plot_type='o-',
             numpoints=1,
             y_label=u"Wartość $\mathbf{SD1_d}$/$\mathbf{SD1_a}$ [ms]",
             percentage=True),
        Spec((get_idx(headers, 'sd2d'), get_idx(headers, 'sd2a'), t_idx),
             ["SD2_d", "SD2_a"], file_, title=u"(B) Zmienność długoterminowa",
             plot_type='o-',
             numpoints=1,
             y_label=u"Wartość $\mathbf{SD2_d}$/$\mathbf{SD2_a}$ [ms]",
             percentage=True),
        Spec((get_idx(headers, 'sdnnd'), get_idx(headers, 'sdnna'), t_idx),
             ["SDNN_d", "SDNN_a"], file_, title=u"(C) Zmienność całkowita",
             time_label=True,
             plot_type='o-',
             numpoints=1,
             y_label=u"Wartość $\mathbf{SDNN_d}$/$\mathbf{SDNN_a}$ [ms]",
             percentage=True),
        ]

    ss = len(specs)
    height_ratios = [4]
    height_ratios.extend([(100 - height_ratios[0]) / ss] * ss)
    # print 'height_ratios: ', height_ratios

    gs = gridspec.GridSpec(
                           # 5,
                           ss + 1,
                           1,
                           height_ratios=height_ratios
                           )
    # gs.update(left=0.03, right=0.98, hspace=0.15, wspace=0.9)
    gs.update(left=0.04, right=0.99, wspace=0.1, hspace=0.2, bottom=0.04, top=0.97)

    num_plot = (len(specs) + 1) * 100 + 10
    num_plot = num_plot + 1

    create_ax_title(gs)

    sharex = None

    for idx, spec in enumerate(specs):
        if spec.usecols.count(-1) > 0:
            continue
        # print('idx: ' + str(idx))
        des2 = None
        if len(spec.usecols) == 3:
            des1, des2, timing = np.loadtxt(spec.file_, usecols=spec.usecols,
                                skiprows=1, delimiter=';', unpack=True)  # @IgnorePep8
        else:
            if spec.annotation:
                des1, annotation = np.loadtxt(spec.file_, usecols=spec.usecols,
                                skiprows=1,
                                # delimiter=';',
                                unpack=True)
                # odfiltrowanie adnotacji
                if (len(pl.array(pl.find(annotation != 0)) > 0)):
                    des1 = des1[pl.array(pl.find(annotation == 0))]
                timing = np.cumsum(des1)
            else:
                des1, timing = np.loadtxt(spec.file_, usecols=spec.usecols,
                                skiprows=1, delimiter=';', unpack=True)  # @IgnorePep8

        if timing[-1:] > 3600000:
            time_unit = 'godziny'
            timing = timing / 3600000
        elif timing[-1:] > 60000:
            time_unit = 'minuty'
            timing = timing / 60000

        num_plot = num_plot + 1
        if not sharex == None and spec.share_plot == True:
            # ax = fig.add_subplot(num_plot, sharex=sharex)
            ax = plt.subplot(gs[idx + 1], sharex=sharex)
        else:
            # ax = fig.add_subplot(num_plot)
            ax = plt.subplot(gs[idx + 1])
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
        if len(spec.labels) == 1 and not spec.value == None:
            des1_count = len(np.where(des1 > spec.value)[0])

        if spec.title:
            font_1 = font_0.copy()
            font_1.set_size('18')
            font_1.set_weight('bold')

            #ax.text(np.mean(timing) , des1_max, spec.title, fontproperties=font_1) # size=15)
            ax.text(0.5, 0.9, spec.title, fontproperties=font_1, transform=ax.transAxes)

        ax.plot(timing, des1, spec.plot_type)
        if len(spec.labels) == 2:
            ax.plot(timing, des2, spec.plot_type)
            if spec.mean_line:
                ax.axhline(des1_mean, lw=3, color='red')
                ax.axhline(des2_mean, lw=3, color='green')
        else:
            ax.axhline(des1_mean, lw=3, color='black')

        if len(spec.labels) == 2:
            des2_min = np.min(des2)
            des2_max = np.max(des2)

            des_min = np.round(np.max([des1_min, des2_min]), decimals=1)
            des_max = np.round(np.max([des1_max, des2_max]), decimals=1)
        else:
            des_min = des1_min
            des_max = des1_max

        max_timing = np.max(timing)
        # print('max_timing: ' + str(max_timing))

        if spec.share_plot == False:
            ax.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
        ax.xaxis.set_ticks(np.arange(0, int(max_timing) + 1, 1))
        ax.set_xlim(0, max_timing)

        leg_spec = {}
        leg_spec["loc"] = 'upper left'
        if spec.numpoints:
            leg_spec["numpoints"] = spec.numpoints

        des1_percentage = 0.0
        des2_percentage = 0.0
        if spec.percentage:
            des1_percentage = des1_count / (1.0 * (des1_count + des2_count))
            des2_percentage = des2_count / (1.0 * (des1_count + des2_count))
        #print(des1_percentage, des2_percentage)
        if len(spec.labels) == 2:
            if spec.mean_line:
                if spec.percentage:
                    leg = ax.legend([u"$\mathbf{%s}$ Całkowity udział [%4.2f] Średnia [%i]" % (spec.labels[0], des1_percentage, des1_mean),
                                 u"$\mathbf{%s}$ Całkowity udział [%4.2f] Średnia [%i]" % (spec.labels[1], des2_percentage, des2_mean),],
                                **leg_spec)
                else:
                    leg = ax.legend([u"$\mathbf{%s}$ Ilość [%i] Średnia [%i]" % (spec.labels[0], des1_count, des1_mean),
                                 u"$\mathbf{%s}$ Ilość [%i] Średnia [%i]" % (spec.labels[1], des2_count, des2_mean),],
                                **leg_spec)
            else:
                if spec.percentage:
                    leg = ax.legend([u"$\mathbf{%s}$ Całkowity udział [%4.2f]" % (spec.labels[0], des1_percentage),
                                     u"$\mathbf{%s}$ Całkowity udział [%4.2f]" % (spec.labels[1], des2_percentage),],
                                    **leg_spec)
                else:
                    leg = ax.legend([u"$\mathbf{%s}$ Ilość [%i]" % (spec.labels[0], des1_count),
                                     u"$\mathbf{%s}$ Ilość [%i]" % (spec.labels[1], des2_count),],
                                    **leg_spec)
        else:
            if spec.value is None:
                leg = ax.legend(['$\mathbf{%s}$' % (spec.labels[0])],
                                **leg_spec)
            else:
                leg = ax.legend([u"$\mathbf{%s}$ Ilość [%i]" % (spec.labels[0], des1_count)],
                                **leg_spec)
        bold_legend(leg)

        font_1 = font_0.copy()
        font_1.set_size('14')
        font_1.set_weight('bold')

        if spec.time_label:
            ax.set_xlabel(u"Czas [%s]" % time_unit, fontproperties=font_1)
        ax.set_ylabel(spec.y_label, fontproperties=font_1)

        bold_ticks_labels(ax)

    if save_plot:
        path = fs.dirname(file_)
        png_filename = os.path.basename(file_) + ".png"
        png_file = fs.normpath(fs.join(path, png_filename))
        png_file = "/tmp/hrv_1_24h_skokowo.png" if skokowo else "/tmp/hrv_1_24h.png"
        plt.savefig(png_file)
        print('Plot: ' + str(png_file) + ' saved.')
    else:
        plt.show()
    plt.clf()


for source in sources:
    generate_asymmetry_changes(source.file_, source.file_rr)
