#!/usr/bin/env python
# coding: utf-8

'''
Created on Nov 26, 2013

@author: jurek
'''


import sys
import matplotlib
#matplotlib.use('GTK')
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import Image
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D

#COMMENT
#pl.rc('text', usetex=True)
#pl.rc('text.latex',unicode=True)

font_0 = FontProperties('DejaVu Sans')

preamble = [
            '\usepackage[polish]{babel}',
            #'\usepackage[utf8]{inputenc}',
            #'\usepackage[T1]{polski}'
            ]
preamble = [
            '\usepackage[polish]{babel}',
            '\usepackage[utf8]{inputenc}'
            #'\usepackage[utf8]{fontenc}',
            #'\usepackage[utf8]{inputenc}',
            #'\usepackage[english,polish]{babel}',
            #'\usepackage{polski}'
            #'\usepackage[T1]{polski}'
            ]
###pylab.rc('text.latex',preamble=preamble)
#pl.rc('text.latex',preamble='\usepackage[T1]{polski}') # oryg

#COMMENT
#pl.rc('text.latex',preamble=preamble) # v2

#pylab.rc('text.latex',preamble='\usepackage[T1]{fontenc}')
#pylab.rc('text.latex',preamble='\usepackage{polski}')

#COMMENT
#pl.rcParams['text.latex.preamble'] = [r'\boldmath']


from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches


def make_ticklabels_invisible(fig):
    return
    for i, ax in enumerate(fig.axes):
        #ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)


def join_lines(ax, min_idx, max_idx, y, color='black'):
    codes = [Path.MOVETO] + [Path.LINETO]
    vertices = [(min_idx, y), (max_idx, y)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor=color, zorder=3, lw=4)
    pathpatch.set_fill(False)
    ax.add_patch(pathpatch)


def draw_line_1(ax, idx, y_min, y_max, color='black', zorder=3):
    codes = [Path.MOVETO] + [Path.LINETO]
    vertices = [(idx, y_max), (idx, y_min)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor=color, zorder=zorder, lw=4)
    pathpatch.set_fill(False)
    ax.add_patch(pathpatch)


def draw_box_with_text(ax, x, y, width, height, text, color='black', zorder=3, text_fontsize=15,
                       text_color="black"):

    alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}

    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')

    codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
    vertices = [(x, y), (x + width, y), (x + width, y - height), (x, y - height), (0, 0)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor=color, zorder=zorder, lw=4)
    pathpatch.set_fill(False)
    ax.text(x + width / 2.0, y - height / 2.0,
            text,
            color=text_color,
            fontproperties=font_1,
            **alignment)
    ax.add_patch(pathpatch)


def draw_simple_arrow(ax, posA=None, posB=None, path=None, tail_width=5, head_width=None, head_length=10,
                    color="black", label="", text=None, text_fontsize=14, x_text_pos=None, y_text_pos=None,
                    text_color="black"):
    arrow_down = mpatches.FancyArrowPatch(posA=posA, posB=posB, path=path, color=color, label=label, lw=3.0)
    arrow_down.set_fill(False)
    if head_width == None and not tail_width == None:
        head_width = 3 * tail_width
    arrowstyle =mpatches.ArrowStyle.Simple(head_length=head_length, head_width=head_width, tail_width=tail_width)
    arrow_down.set_arrowstyle(arrowstyle)
    ax.add_patch(arrow_down)
    if not text == None:
        if x_text_pos == None and posA[0] == posA[0]:
            x_text_pos = posA[0]
        if y_text_pos == None and posA[0] == posA[0]:
            y_text_pos = posB[1] + (posA[1] - posB[1]) / 2
        alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}

        font_1 = font_0.copy()
        font_1.set_size(text_fontsize)
        font_1.set_weight('bold')

        ax.text(x_text_pos, y_text_pos, text,
                #fontsize=text_fontsize,
                color=text_color,
                fontproperties=font_1,
                **alignment)


def draw_simple_ellipse(ax, x, y, width, height, angle=0.0, color="black", label="",
                    text=None, text_fontsize=14, x_text_pos=None, y_text_pos=None, fill=False):
    ellipse = mpatches.Ellipse((x, y), width, height, angle=angle, color=color, label=label, lw=3.0)
    ellipse.set_fill(fill)
    ax.add_patch(ellipse)

    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')

    if not text == None:
        if x_text_pos == None:
            x_text_pos = x
        if y_text_pos == None:
            y_text_pos = y
        alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}
        ax.text(x_text_pos, y_text_pos, text,
                #fontsize=text_fontsize,
                fontproperties=font_1,
                **alignment)


def create_empty_plot(gs1, row_number):
    # empty plot
    empty_plot = plt.subplot(gs1[row_number,0])
    empty_plot.set_ylim(0, 20)
    empty_plot.set_xlim(0, max_timing)
    empty_plot.grid(False)
    empty_plot.set_frame_on(False)
    empty_plot.title.set_visible(False)
    empty_plot.xaxis.set_major_locator(plt.NullLocator())
    empty_plot.yaxis.set_major_locator(plt.NullLocator())
    for tl in empty_plot.get_xticklabels():
        tl.set_visible(False)
    for tl in empty_plot.get_yticklabels():
        tl.set_visible(False)
    return row_number + 1


def get_min_idx(idxs, shift=1):

    for idx in idxs:
        if not (idx % shift == 0):
            continue
        return idx + shift / 2.0
    return 0 + shift / 2.0


def get_max_idx(idxs, shift=1):
    m_idx = max_idx
    for idx in idxs:
        if not (idx % shift == 0):
            continue
        m_idx = idx
    return m_idx + shift / 2.0


def can_show(show_rows, idx):
    return True if idx < len(show_rows) and show_rows[idx] else False


def change_ticks_for_5_minutes(ax):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    f.canvas.draw()
    # change x labels for every 5 minute
    x_labels = [str(int(item.get_text()) * 5) for item in ax.get_xticklabels()]
    ax.set_xticklabels(x_labels)


def bold_ticks_labels(ax, fontsize=10):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    f.canvas.draw()
    x_labels = [item.get_text() for item in ax.get_xticklabels()]
    y_labels = [item.get_text() for item in ax.get_yticklabels()]
    font_1 = font_0.copy()
    font_1.set_size(fontsize)
    font_1.set_weight('bold')
    ax.set_xticklabels(x_labels, fontproperties=font_1)
    ax.set_yticklabels(y_labels, fontproperties=font_1)


f = plt.figure(figsize=(17, 21))
#f = plt.figure()
#print(f.get_figheight(), f.get_figwidth())

#start_hour = None
start_hour = 11
stop_hour = 13

font_1 = font_0.copy()
font_1.set_size('20')
font_1.set_weight('bold')
plt.suptitle(u"Schemat wyznaczania HRA dla pojedynczego 24-godzinnego nagrania odstępów RR.",
            fontproperties=font_1, y=0.995, fontsize=25)

empty_ratio = 0.2
if start_hour == None:
    max_idx = 23
    all_ratios = [1.0, empty_ratio, 0.4, empty_ratio,  1.0, empty_ratio,
              0.5, empty_ratio, 1.0, 2.0]
    tachogram_label_pos = 18
else:
    max_idx = 24
    all_ratios = [1.0, 0.4, 1.0, empty_ratio,
                  0.5, empty_ratio, 1.0, 2.0]
    tachogram_label_pos = 17

show_rows = [True] * len(all_ratios)
height_ratios = [all_ratios[idx] for idx, s in enumerate(show_rows) if s == True]
num_rows = len([s for s in show_rows if s == True])
num_cols = 1

row_number = 0

#plt.suptitle("GirdSpec w/ different subplotpars")

gs1 = GridSpec(num_rows, num_cols, height_ratios=height_ratios) #[3, 0.3, 3, 0.5, 4])
#gs1.update(left=0.05, right=0.48, wspace=0.05)
gs1.update(left=0.04, right=0.99, wspace=0.1, hspace=0.0, bottom=0.04, top=0.98)

file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/jakubas_RR_P.rea"
usecols = (1, 2,)
des1, annotation = np.loadtxt(file_rr, usecols=usecols, skiprows=1, unpack=True)

#odfiltrowanie adnotacji
if (len(pl.array(pl.find(annotation != 0)) > 0)):
    des1 = des1[pl.array(pl.find(annotation == 0))]

timing_0 = np.cumsum(des1)
#print('timing_0: ', timing_0)
timing = timing_0 / 3600000
des1_max = np.max(des1)
des1_min = np.min(des1)
max_timing = np.max(timing)

window_step = 1 # 1 hour
sym_indexes = [1, 5, 6, 12, 21] # only multiple of window_step are allowed

#font0 = FontProperties()

slice_color = "black"

if can_show(show_rows, row_number):
    ax_tachogram = plt.subplot(gs1[row_number, :])
    ax_tachogram.set_color_cycle(['blue'])
    ax_tachogram.plot(timing, des1)
    ax_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing) + 1, 1))
    ax_tachogram.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    y_lim = ax_tachogram.get_ylim()[1]
    if not start_hour == None:
        codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
        vertices = [(start_hour, y_lim - 20),
                    (stop_hour, y_lim - 20),
                    (stop_hour, 0),
                    (start_hour, 0), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
        pathpatch.set_fill(False)
        ax_tachogram.add_patch(pathpatch)


    #ax_tachogram.legend(['$\mathbf{%s}$' % ("RR")], loc='upper left')
    #ax_tachogram.set_xlabel(r'\large{Czas [godziny]}')
    #ax_tachogram.set_ylabel(r'\large{Wartość [ms]}')

    ax_tachogram.legend(['$\mathbf{%s}$' % ("RR")], loc='upper left')
    #ax_tachogram.legend(u"RR", loc='upper left', fontproperties = font_1)
    ax_tachogram.set_xlabel(u"Czas [godziny]", fontproperties = font_1)
    ax_tachogram.set_ylabel(u"Wartość [ms]", fontproperties = font_1)

    #ax_tachogram.set_text(0.8, 0.8, 'Tachogram')
    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')
    #max_idx - max_idx / 11.8
    ax_tachogram.text(tachogram_label_pos, y_lim - 100,
                      u"Tachogram - 24 godziny", fontproperties = font_1
                      #size=20
                      )
    bold_ticks_labels(ax_tachogram)
    row_number = row_number + 1

if can_show(show_rows, row_number):
    # empty plot
    if start_hour == None:
        row_number = create_empty_plot(gs1, row_number)

if can_show(show_rows, row_number):
    ax_arrow_down = plt.subplot(gs1[row_number, :])
    ax_arrow_down.set_axis_off()
    ax_arrow_down.set_frame_on(False)
    ax_arrow_down.set_xlim(0, max_timing)

    alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}
    text_fontsize = 18

    if start_hour == None:
        tail_width = 800
        head_width = tail_width + tail_width / 5.0
        head_length = 70
        draw_simple_arrow(ax_arrow_down, posA=(max_idx / 2.0, 1.0), posB=(max_idx / 2.0, 0.0),
                       tail_width=tail_width, head_width=head_width,
                       head_length=head_length, #color="brown",
                       text=u"Zastosowanie 5-minutowego okna danych",
                       text_fontsize=text_fontsize,
                       )
    else:
        font_1 = font_0.copy()
        font_1.set_size(text_fontsize)
        font_1.set_weight('bold')

        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = [(start_hour, 1.0), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
        pathpatch.set_fill(False)
        ax_arrow_down.add_patch(pathpatch)

        codes = [Path.MOVETO] + [Path.LINETO]
        vertices = [(stop_hour, 1.0), (max_timing, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
        pathpatch.set_fill(False)
        ax_arrow_down.add_patch(pathpatch)




        ax_arrow_down.text(stop_hour-1, 0.3, u"Zastosowanie 5-minutowego okna danych",
                          fontproperties=font_1,
                          **alignment
                          #size=20
                          )

    row_number = row_number + 1


if can_show(show_rows, row_number):
    if start_hour == None:
        # empty plot
        row_number = create_empty_plot(gs1, row_number)


if can_show(show_rows, row_number):
    # RIGHT TACHOGRAM START
    ax_tachogram_1 = plt.subplot(gs1[row_number,0])
    ax_tachogram_1.set_color_cycle(['blue', 'red'])

    if not start_hour == None:
        # create slice of 24 recording
        start_time = start_hour * 60 * 60 * 1000 # 10 hour
        stop_time = stop_hour * 60 * 60 * 1000  # 12 hour
        start_idx = np.where(timing_0 >= start_time)[0][0]
        stop_idx = np.where(timing_0 >= stop_time)[0][0]

        des1 = des1[start_idx:stop_idx]
        timing = np.cumsum(des1)
        timing = timing / (5*60*1000) # 5 minute

        des1_max = np.max(des1)
        des1_min = np.min(des1)
        max_timing = np.max(timing)


    ax_tachogram_1.plot(timing, des1)
    ax_tachogram_1.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_tachogram_1.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_tachogram_1.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    if start_hour == None:
        x_label = u"Czas [godziny]"
    else:
        x_label = u"Czas [minuty]"
    ax_tachogram_1.set_xlabel(x_label, fontproperties = font_1)
    ax_tachogram_1.set_ylabel(u"Wartość [ms]", fontproperties = font_1)

    #ax_tachogram_1.set_xlabel(r'\large{Czas [godziny]}')
    #ax_tachogram_1.set_ylabel(r'\large{Wartość [ms]}')

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    y_lim = ax_tachogram_1.get_ylim()[1]
    if start_hour == None:
        tach_label = u"Tachogram - 24 godziny"
    else:
        tach_label = u"Tachogram - fragment 2 godziny"
    ax_tachogram_1.text(tachogram_label_pos, y_lim - 100,
                      tach_label, fontproperties=font_1
                      #size=20
                      )
    #ax_tachogram_1.legend(numpoints=10)

    first_lw = 0.5
    lws = np.linspace(first_lw, 4, max_idx + 1 + first_lw)[::-1]

    for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
        if not (idx % window_step == 0):
            continue
        codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
        vertices = [(idx, des1_max - des1_max / 10),
                    (idx + window_step, des1_max - des1_max / 10),
                    (idx + window_step, des1_min + des1_max / 10),
                    (idx, des1_min + des1_max / 10), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor='red', zorder=3, lw=lw)
        pathpatch.set_fill(False)
        ax_tachogram_1.add_patch(pathpatch)
    ax_tachogram_1.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 5 minut"], loc='upper left', numpoints=5)


    arrow_size = 4
    arrow_window_right = mpatches.Arrow(max_idx / 2 - arrow_size / 2,
                                        des1_max - des1_max / 35,
                                        4, 0,
                                        width=100, color="red") #, zorder=3)
    arrow_window_right.set_fill(True)
    ax_tachogram_1.add_patch(arrow_window_right)

    if not start_hour == None:
        change_ticks_for_5_minutes(ax_tachogram_1)
    bold_ticks_labels(ax_tachogram_1)

    row_number = row_number + 1


if can_show(show_rows, row_number):
    # empty plot
    row_number = create_empty_plot(gs1, row_number)


if can_show(show_rows, row_number):
    ax_arrow_down = plt.subplot(gs1[row_number, :])
    ax_arrow_down.set_axis_off()
    ax_arrow_down.set_frame_on(False)

    tail_width = 1100
    head_width = tail_width + tail_width / 5.0
    head_length = 70
    txt = u"Obliczanie deskryptorów asymetrii: $\mathbf{SD1_d,\,SD1_a,\,SD2_d,\,SD2_a,\,SDNN_d,\,SDNN_a}$"
    draw_simple_arrow(ax_arrow_down, posA=(0.5, 1.0), posB=(0.5, 0.0),
                   tail_width=tail_width, head_width=head_width,
                   head_length=head_length, # color="green",
                   label="Dane z EKG", text=txt,
                   text_fontsize=18,
                   )
    row_number = row_number + 1

if can_show(show_rows, row_number):
    # empty plot
    row_number = create_empty_plot(gs1, row_number)

first_lw = 0.5
lws = np.linspace(first_lw, 4, max_idx + 1 + first_lw)[::-1]
max_lws = max(lws)
lws = [max_lws] * len(lws)

asym_indexes = [idx for idx in range(max_idx) if idx not in sym_indexes]

sym_color = "brown"
asym_color = "green"

if can_show(show_rows, row_number):
    # RIGHT TACHOGRAM START
    ax_tachogram_2 = plt.subplot(gs1[row_number,0])
    ax_tachogram_2.set_color_cycle(['blue', 'red'])
    ax_tachogram_2.plot(timing, des1)
    ax_tachogram_2.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_tachogram_2.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_tachogram_2.xaxis.set_ticks_position('top')
    ax_tachogram_2.xaxis.set_label_position('top')
    ax_tachogram_2.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')


    if start_hour == None:
        x_label = u"Czas [godziny]"
    else:
        x_label = u"Czas [minuty]"
    ax_tachogram_2.set_xlabel(x_label, fontproperties = font_1)
    ax_tachogram_2.set_ylabel(u"Wartość [ms]", fontproperties = font_1)

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    #ax_tachogram_2.set_xlabel(r'\large{Czas [godziny]}')
    #ax_tachogram_2.set_ylabel(r'\large{Wartość [ms]}')

    if start_hour == None:
        tach_label = u"Tachogram - 24 godziny"
    else:
        tach_label = u"Tachogram - fragment 2 godziny"

    y_lim = ax_tachogram_2.get_ylim()[1]
    ax_tachogram_2.text(tachogram_label_pos, y_lim - 100,
                      tach_label, fontproperties=font_1)

    for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
        #if idx % window_step == 1:
        if not (idx % window_step == 0):
            continue
        vertices = []
        codes = []
        codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
        vertices = [(idx, des1_max - des1_max / 10),
                    (idx + window_step, des1_max - des1_max / 10),
                    (idx + window_step, des1_min + des1_max / 10),
                    (idx, des1_min + des1_max / 10), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor='red', zorder=3, lw=lw)
        pathpatch.set_fill(False)
        ax_tachogram_2.add_patch(pathpatch)

    min_y = 50
    max_y = 400

    zero_ones = [("0" if idx in sym_indexes else "A") for idx in range(max_idx)]

    zero_one_y = des1_min - 50

#     font_zero_one = font0.copy()
#     font_zero_one.set_style('italic')
#     #font_zero_one.set_weight('bold')
#     font_zero_one.set_size('x-large')

    alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}
    #zero_one_font_size = 20

    font_1 = font_0.copy()
    font_1.set_size('20')
    font_1.set_weight('bold')

    for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
        if not (idx % window_step == 0):
            continue
        codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]

        vertices = [(idx, max_y),
                    (idx + window_step, max_y),
                    (idx + window_step, min_y),
                    (idx, min_y), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor='black', zorder=3, lw=0)
        pathpatch.set_fill(False)


        ax_tachogram_2.text(idx + window_step / 2.0, zero_one_y,
                            u"%s" % (zero_ones[idx]),
                            #size=zero_one_font_size,
                            color=asym_color if idx in asym_indexes else sym_color,
                            fontproperties=font_1,
                            **alignment)
        ax_tachogram_2.add_patch(pathpatch)



    leg = ax_tachogram_2.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 5 minut "],
                           loc='upper left', numpoints=5)
    ax_tachogram_2.add_artist(leg)

    line = Line2D(range(1), range(1), linestyle='None', marker='None', color="blue")
    label = 'Oznaczenia: $\mathbf{%s}$ - asymetria, $\mathbf{%s}$ - brak asymetrii' % ("A", "0")
    leg = ax_tachogram_2.legend([line], [label] , loc='upper center')
    ax_tachogram_2.add_artist(leg)

    if not start_hour == None:
        change_ticks_for_5_minutes(ax_tachogram_2)
    bold_ticks_labels(ax_tachogram_2)

    row_number = row_number + 1


#shapes plot
if can_show(show_rows, row_number):

    y_max_shapes = 4450

    ax_shapes = plt.subplot(gs1[row_number,0])
    ax_shapes.set_ylim(0, y_max_shapes)
    ax_shapes.set_xlim(0, max_timing)
    ax_shapes.grid(False)
    ax_shapes.set_frame_on(False)
    ax_shapes.title.set_visible(False)
    ax_shapes.xaxis.set_major_locator(plt.NullLocator())
    ax_shapes.yaxis.set_major_locator(plt.NullLocator())
    for tl in ax_shapes.get_xticklabels():
        tl.set_visible(False)
    for tl in ax_shapes.get_yticklabels():
        tl.set_visible(False)

    sym_shift = 300
    asym_shift = 2 * sym_shift
    for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
        if not (idx % window_step == 0):
            continue
        if idx in sym_indexes:
            draw_line_1(ax_shapes, idx + window_step / 2.0, y_max_shapes - sym_shift, y_max_shapes,
                        color=sym_color)
        else:
            draw_line_1(ax_shapes, idx + window_step / 2.0, y_max_shapes - asym_shift, y_max_shapes,
                        color=asym_color, zorder=4)

    join_lines(ax_shapes, get_min_idx(asym_indexes, shift=window_step),
                        get_max_idx(asym_indexes, shift=window_step),
                        y_max_shapes - asym_shift, color=asym_color)
    join_lines(ax_shapes, get_min_idx(sym_indexes, shift=window_step),
                        get_max_idx(sym_indexes, shift=window_step),
                        y_max_shapes - sym_shift, color=sym_color)

    y_shift = max([sym_shift, asym_shift])
    b_y_shift = y_shift + 100
    b_height = 600
    x_sym = get_min_idx(sym_indexes, shift=0.5)
    y_sym = y_max_shapes - y_shift - b_y_shift
    b_width = 5

    txt = '%s' % (u"Licznik okien bez asymetrii")
    draw_box_with_text(ax_shapes, x_sym, y_sym, b_width, b_height, txt, color=sym_color,
                       text_color=sym_color)

    x_asym = get_max_idx(asym_indexes, shift=0.5)
    txt = '%s' % (u"Licznik okien z asymetrią")
    draw_box_with_text(ax_shapes, x_asym, y_sym, -b_width, b_height, txt, color=asym_color,
                       text_color=asym_color)

    arrow_sym_x = 4.0
    draw_simple_arrow(ax_shapes, #path=path,
                   posA=(arrow_sym_x, y_max_shapes - sym_shift),
                   posB=(arrow_sym_x, y_sym),
                   text=u"%s" % (len(sym_indexes)),
                   tail_width=40,
                   color=sym_color,
                   text_color=sym_color,
                   head_length=20,
                   )
    arrow_asym_x = 20.0
    draw_simple_arrow(ax_shapes, #path=path,
                   posA=(arrow_asym_x, y_max_shapes - asym_shift),
                   posB=(arrow_asym_x, y_sym),
                   text=u"%s" % (len(asym_indexes)),
                   tail_width=40,
                   color=asym_color,
                   text_color=asym_color,
                   head_length=20,
                   )

    txt = u"Test binomialny"
    binomial_color = "black"
    t_b_width = b_width + 2
    t_b_height = b_height + 200
    x_binomial = max_idx / 2 -  t_b_width / 2
    draw_box_with_text(ax_shapes, x_binomial, y_sym, t_b_width, t_b_height, txt, color=binomial_color,
                       text_fontsize=20)

    #left binomial arrow
    draw_simple_arrow(ax_shapes, #path=path,
                   posA=(x_binomial, y_sym - b_height/2.0),
                   posB=(x_sym + b_width, y_sym - b_height/2.0),
                   tail_width=5,
                   color=binomial_color,
                   head_length=25,
                   )

    #right binomial arrow
    draw_simple_arrow(ax_shapes, #path=path,
                   posA=(x_binomial + t_b_width, y_sym - b_height/2.0),
                   posB=(x_asym - b_width, y_sym - b_height/2.0),
                   tail_width=5,
                   color=binomial_color,
                   head_length=25,
                   )

    outcome_color = "orange"
    # outcome arrow
    x_outcome = x_binomial + t_b_width / 2.0
    o_height = 700
    y_outcome_shift = 50
    draw_simple_arrow(ax_shapes, #path=path,
                   posA=(x_outcome, y_sym - t_b_height - y_outcome_shift),
                   posB=(x_outcome, y_sym - t_b_height - y_outcome_shift - o_height),
                   text=u"Wynik",
                   tail_width=150,
                   color=outcome_color,
                   head_length=40,
                   text_fontsize=20,
                   )

    # outcome ellipse
    e_width = 8
    e_height = 1500
    e_shift = 50
    e_y = y_sym - t_b_height - o_height - e_height / 2 - e_shift - y_outcome_shift
    draw_simple_ellipse(ax_shapes, x_outcome, e_y, e_width, e_height, color=outcome_color,
                    text=u"Asymetria \n lub \n brak asymetrii \n dla pojedynczego nagrania",
                    text_fontsize=20,
                    fill=True)

    row_number = row_number + 1

make_ticklabels_invisible(plt.gcf())

file_ = "/tmp/schemat_HRA_1.png"
plt.savefig(file_)
print('Save into ', file_)
#plt.show()

