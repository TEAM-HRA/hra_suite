#!/usr/bin/env python
# coding: utf-8

'''
Created on Nov 26, 2013

@author: jurek
'''


import sys
import matplotlib
# matplotlib.use('GTK')
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
import glob
# from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable

# COMMENT
# pl.rc('text', usetex=True)
# pl.rc('text.latex',unicode=True)

font_0 = FontProperties('DejaVu Sans')

preamble = ['\usepackage[polish]{babel}',
            # '\usepackage[utf8]{inputenc}',
            # '\usepackage[T1]{polski}'
            ]
preamble = ['\usepackage[polish]{babel}',
            '\usepackage[utf8]{inputenc}'
            # '\usepackage[utf8]{fontenc}',
            # '\usepackage[utf8]{inputenc}',
            # '\usepackage[english,polish]{babel}',
            # '\usepackage{polski}'
            # '\usepackage[T1]{polski}'
            ]
# pylab.rc('text.latex',preamble=preamble)
# pl.rc('text.latex',preamble='\usepackage[T1]{polski}') # oryg

# COMMENT
# pl.rc('text.latex',preamble=preamble) # v2

# pylab.rc('text.latex',preamble='\usepackage[T1]{fontenc}')
# pylab.rc('text.latex',preamble='\usepackage{polski}')

# COMMENT
# pl.rcParams['text.latex.preamble'] = [r'\boldmath']


from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

save_fig = True

# def make_ticklabels_invisible(fig):
#     return
#     for i, ax in enumerate(fig.axes):
#         #ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
#         for tl in ax.get_xticklabels() + ax.get_yticklabels():
#             tl.set_visible(False)


def set_border(ax):
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)

    ax.spines['top'].set_linewidth(0.5)
    ax.spines['right'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['left'].set_linewidth(0.5)

    ax.set_frame_on(True)


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
                       text_color="black", edgecolor='black', linewidth=4, linestyle=None):

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}

    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')

    codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
    vertices = [(x, y), (x + width, y), (x + width, y - height), (x, y - height), (0, 0)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(
        path, #facecolor='None',
        edgecolor=edgecolor, zorder=zorder,# lw=linewidth,
        linewidth=linewidth, linestyle=linestyle
    )
    pathpatch.set_fill(False)
    ax.text(x + width / 2.0, y - height / 2.0,
            text,
            color=text_color,
            fontproperties=font_1,
            **alignment)
    ax.add_patch(pathpatch)


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
        alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
        ax.text(x_text_pos, y_text_pos, text,
                # fontsize=text_fontsize,
                fontproperties=font_1,
                **alignment)


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


def change_ticks_for_5_minutes(ax):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    f.canvas.draw()
    # change x labels for every 5 minute
    x_labels = [str(int(item.get_text()) * 5) for item in ax.get_xticklabels()]
    ax.set_xticklabels(x_labels)


def bold_ticks_labels(ax, fontsize=11):
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


def get_24h_data():

    file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/jakubas_RR_P.rea"
    usecols = (1, 2,)
    des1, annotation = np.loadtxt(file_rr, usecols=usecols, skiprows=1, unpack=True)

    # odfiltrowanie adnotacji
    if (len(pl.array(pl.find(annotation != 0)) > 0)):
        des1 = des1[pl.array(pl.find(annotation == 0))]
        timing_0 = np.cumsum(des1)

    unit = 60*60*1000  # 1h
    timing = np.cumsum(des1)
    timing = timing / unit
    return des1, timing, timing_0


def get_5m_data(des1, timing_0, start_hour, stop_hour):
    unit = 5*60*1000  # 5 minute expressed in miliseconds
    # create slice of 24 recording
    start_time = start_hour * 60 * 60 * 1000  # hours expressed in miliseconds
    stop_time = stop_hour * 60 * 60 * 1000  # hours expressed in miliseconds
    start_idx = np.where(timing_0 >= start_time)[0][0]
    stop_idx = np.where(timing_0 >= stop_time)[0][0]
    des1 = des1[start_idx:stop_idx]

    timing = np.cumsum(des1)
    timing = timing / unit

    return des1, timing


def change_xtickslabels_2_hours(ax, fontsize=11):
    # We need to draw the canvas, otherwise the labels won't be positioned and
    # won't have values yet.
    f.canvas.draw()

    font_h = font_0.copy()
    font_h.set_size(fontsize + 3)
    font_h.set_weight('bold')

    hour_idx = start_hour
    x_labels = []
    for item in ax.get_xticklabels():
        value = int(item.get_text())
        if value % 60 == 0:
            x_labels.append(str(hour_idx) + 'h')
            item.set_fontproperties(font_h)
            hour_idx += 1
        elif value > 60:
            value = value % 60
            x_labels.append(value)
        else:
            x_labels.append(item.get_text())

    ax.set_xticklabels(x_labels)


def is_only_2_hours(start_hour, stop_hour):
    if not start_hour == None and not stop_hour == None:
        return stop_hour - start_hour == 2
    return False


def create_simple_tachogram(gs1, row_number, timing, des1,
                            slice_color="black", show_window=False,
                            start_hour=None, stop_hour=None):

    max_timing = np.max(timing)
    only_2_hours = is_only_2_hours(start_hour, stop_hour)

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
    if show_window and not start_hour == None:
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

    if only_2_hours:
        tachogram_label_pos = 17
        tachogram_title = u"Tachogram - fragment 2 godziny"
        x_label = u"Czas [minuty]"
    else:
        tachogram_label_pos = 19
        tachogram_title = u"Tachogram - 24 godziny"
        x_label = u"Czas [godziny]"

    leg = ax_tachogram.legend(['$\mathbf{%s}$' % ("RR")], loc='upper left')
    # change legend font properties
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    ax_tachogram.set_xlabel(x_label, fontproperties=font_1)
    ax_tachogram.set_ylabel(u"Wartość [ms]", fontproperties=font_1)

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    ax_tachogram.text(tachogram_label_pos, y_lim - 100,
                      tachogram_title, fontproperties=font_1)

    if not start_hour == None:
        change_ticks_for_5_minutes(ax_tachogram)
    bold_ticks_labels(ax_tachogram)
    if only_2_hours == True:
        change_xtickslabels_2_hours(ax_tachogram)

    return row_number + 1


def create_zoom_plot(gs1, row_number, timing,
                     start_hour=None, stop_hour=None,
                     slice_color="black"):

    max_timing = np.max(timing)

    ax_zoom = plt.subplot(gs1[row_number, :])
    ax_zoom.set_axis_off()
    ax_zoom.set_frame_on(False)
    ax_zoom.set_xlim(0, max_timing)

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
    text_fontsize = 18

    font_1 = font_0.copy()
    font_1.set_size(text_fontsize)
    font_1.set_weight('bold')

    codes = [Path.MOVETO] + [Path.LINETO]
    vertices = [(start_hour, 1.0), (0, 0)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
    pathpatch.set_fill(False)
    ax_zoom.add_patch(pathpatch)

    codes = [Path.MOVETO] + [Path.LINETO]
    vertices = [(stop_hour, 1.0), (max_timing, 0)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
    pathpatch.set_fill(False)
    ax_zoom.add_patch(pathpatch)

#     ax_zoom.text(stop_hour-1, 0.3, u"2-godzinny wycinek tachogramu",
#                       fontproperties=font_1,
#                       **alignment
#                       #size=20
#                       )

    return row_number + 1


def create_arrow_plot_5m(gs1, row_number, timing, max_idx=None):
    max_timing = np.max(timing)

    ax_arrow_plot = plt.subplot(gs1[row_number, :])
    ax_arrow_plot.set_axis_off()
    ax_arrow_plot.set_frame_on(False)
    ax_arrow_plot.set_xlim(0, max_timing)

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
    text_fontsize = 18

    tail_width = 800
    head_width = tail_width + tail_width / 5.0
    head_length = 70
    draw_simple_arrow(ax_arrow_plot, posA=(max_idx / 2.0, 1.0), posB=(max_idx / 2.0, 0.0),
                      tail_width=tail_width, head_width=head_width,
                      head_length=head_length,  # color="brown",
                      text=u"Zastosowanie 5-minutowego okna danych",
                      text_fontsize=text_fontsize,
                      )
    return row_number + 1


def create_windowed_tachogram(gs1, row_number, timing, des1, max_idx,
                              start_hour=None, stop_hour=None):
    # RIGHT TACHOGRAM START
    ax_windowed_tachogram = plt.subplot(gs1[row_number, 0])
    ax_windowed_tachogram.set_color_cycle(['blue', 'red'])

    max_timing = np.max(timing)
    des1_max = np.max(des1)
    des1_min = np.min(des1)

    only_2_hours = is_only_2_hours(start_hour, stop_hour)

    ax_windowed_tachogram.plot(timing, des1)
    ax_windowed_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_windowed_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_windowed_tachogram.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    if start_hour == None:
        x_label = u"Czas [godziny]"
    else:
        x_label = u"Czas [minuty]"
    ax_windowed_tachogram.set_xlabel(x_label, fontproperties=font_1)
    ax_windowed_tachogram.set_ylabel(u"Wartość [ms]", fontproperties=font_1)

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    y_lim = ax_windowed_tachogram.get_ylim()[1]
    if start_hour == None:
        tachogram_label_pos = 19
        tach_label = u"Tachogram - 24 godziny"
    else:
        tachogram_label_pos = 17
        tach_label = u"Tachogram - fragment 2 godziny"
    ax_windowed_tachogram.text(tachogram_label_pos, y_lim - 100,
                               tach_label, fontproperties=font_1
                               # size=20
                               )

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
        ax_windowed_tachogram.add_patch(pathpatch)
    leg = ax_windowed_tachogram.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 5 minut"], loc='upper left', numpoints=5)
    # change legend font properties
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    arrow_size = 4.5
    head_width = 45
    tail_width = 25
    head_length = 40
    arrow_shift = 100 if start_hour == None else 40
    draw_simple_arrow(ax_windowed_tachogram,
                      posA=(max_idx / 2.0 - arrow_size / 2.0, y_lim - head_width - arrow_shift),
                      posB=(max_idx / 2.0 + arrow_size / 2.0, y_lim - head_width - arrow_shift),
                      tail_width=tail_width, head_width=head_width,
                      head_length=head_length, color="red",
                      text=u"Kierunek przesuwania okna",
                      text_fontsize=12,
                      lw=2.0,
                      )
    if not start_hour == None:
        change_ticks_for_5_minutes(ax_windowed_tachogram)
    bold_ticks_labels(ax_windowed_tachogram)
    if only_2_hours == True:
        change_xtickslabels_2_hours(ax_windowed_tachogram)
    return row_number + 1


def create_descriptors_arrow(gs1, row_number):
    ax_descriptors = plt.subplot(gs1[row_number, :])
    ax_descriptors.set_axis_off()
    ax_descriptors.set_frame_on(False)

    tail_width = 1100
    head_width = tail_width + tail_width / 5.0
    head_length = 70
    txt = u"Obliczanie deskryptorów asymetrii: $\mathbf{SD1_d,\,SD1_a,\,SD2_d,\,SD2_a,\,SDNN_d,\,SDNN_a}$"
    draw_simple_arrow(ax_descriptors, posA=(0.5, 1.0), posB=(0.5, 0.0),
                      tail_width=tail_width, head_width=head_width,
                      head_length=head_length,  # color="green",
                      label="Dane z EKG", text=txt,
                      text_fontsize=18,
                      )
    return row_number + 1


def create_windowed_descriptors_tachogram(gs1, row_number, timing, des1, max_idx,
                                          sym_indexes, start_hour=None, stop_hour=None,
                                          sym_color="brown", asym_color="green"):

    first_lw = 0.5
    lws = np.linspace(first_lw, 4, max_idx + 1 + first_lw)[::-1]
    max_lws = max(lws)
    lws = [max_lws] * len(lws)

    only_2_hours = is_only_2_hours(start_hour, stop_hour)

    asym_indexes = [idx for idx in range(max_idx) if idx not in sym_indexes]

    max_timing = np.max(timing)
    des1_max = np.max(des1)
    des1_min = np.min(des1)

    # RIGHT TACHOGRAM START
    ax_windowed_desc = plt.subplot(gs1[row_number, 0])
    ax_windowed_desc.set_color_cycle(['blue', 'red'])
    ax_windowed_desc.plot(timing, des1)
    ax_windowed_desc.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_windowed_desc.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_windowed_desc.xaxis.set_ticks_position('top')
    ax_windowed_desc.xaxis.set_label_position('top')
    ax_windowed_desc.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('11')
    font_1.set_weight('bold')

    if start_hour == None:
        x_label = u"Czas [godziny]"
    else:
        x_label = u"Czas [minuty]"
    ax_windowed_desc.set_xlabel(x_label, fontproperties=font_1)
    ax_windowed_desc.set_ylabel(u"Wartość [ms]", fontproperties=font_1)

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    if start_hour == None:
        tach_label = u"Tachogram - 24 godziny"
        tachogram_label_pos = 19
    else:
        tach_label = u"Tachogram - fragment 2 godziny"
        tachogram_label_pos = 17

    y_lim = ax_windowed_desc.get_ylim()[1]
    ax_windowed_desc.text(tachogram_label_pos, y_lim - 100,
                          tach_label, fontproperties=font_1)

    for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
        # if idx % window_step == 1:
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
        ax_windowed_desc.add_patch(pathpatch)

    min_y = 50
    max_y = 400

    zero_ones = [("0" if idx in sym_indexes else "A") for idx in range(max_idx)]

    zero_one_y = des1_min - 50

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
    # zero_one_font_size = 20

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

        ax_windowed_desc.text(idx+window_step/2.0, zero_one_y,
                              u"%s" % (zero_ones[idx]),
                              # size=zero_one_font_size,
                              color=asym_color if idx in asym_indexes else sym_color,
                              fontproperties=font_1,
                              **alignment)
        ax_windowed_desc.add_patch(pathpatch)

    leg = ax_windowed_desc.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 5 minut"],
                                  loc='upper left', numpoints=5)
    ax_windowed_desc.add_artist(leg)
    # change legend font properties
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    lines = [3] * Line2D(range(1), range(1), linestyle='None', marker='None', color="blue")
    labels = ['G: - godzina', 'M: - minuta', 'S: - sekunda']
    leg = ax_windowed_desc.legend([lines], [labels], loc='upper right')
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')
    ax_windowed_desc.add_artist(leg)

    if not start_hour == None:
        change_ticks_for_5_minutes(ax_windowed_desc)
    bold_ticks_labels(ax_windowed_desc)

    if only_2_hours == True:
        change_xtickslabels_2_hours(ax_windowed_desc)

    return row_number + 1


def create_shapes_plot(gs1, row_number, timing, max_idx, sym_indexes=None,
                       sym_color="brown", asym_color="green"):

    max_timing = np.max(timing)
    y_max_shapes = 4550
    asym_indexes = [idx for idx in range(max_idx) if idx not in sym_indexes]
    first_lw = 0.5
    lws = np.linspace(first_lw, 4, max_idx + 1 + first_lw)[::-1]
    max_lws = max(lws)
    lws = [max_lws] * len(lws)

    ax_shapes = plt.subplot(gs1[row_number, 0])
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
    draw_simple_arrow(ax_shapes,  # path=path,
                      posA=(arrow_sym_x, y_max_shapes - sym_shift),
                      posB=(arrow_sym_x, y_sym),
                      text=u"%s" % (len(sym_indexes)),
                      tail_width=40,
                      color=sym_color,
                      text_color=sym_color,
                      head_length=20,
                      )
    arrow_asym_x = 20.0
    draw_simple_arrow(ax_shapes,  # path=path,
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
    x_binomial = max_idx / 2 - t_b_width / 2
    draw_box_with_text(ax_shapes, x_binomial, y_sym, t_b_width, t_b_height, txt, color=binomial_color,
                       text_fontsize=20)

    # left binomial arrow
    draw_simple_arrow(ax_shapes,  # path=path,
                      posA=(x_binomial, y_sym - b_height/2.0),
                      posB=(x_sym + b_width, y_sym - b_height/2.0),
                      tail_width=5,
                      color=binomial_color,
                      head_length=25,
                      )

    # right binomial arrow
    draw_simple_arrow(ax_shapes,  # path=path,
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
    draw_simple_arrow(ax_shapes,  # path=path,
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
    e_height = 1650
    e_shift = 50
    e_y = y_sym - t_b_height - o_height - e_height / 2 - e_shift - y_outcome_shift
    draw_simple_ellipse(ax_shapes, x_outcome, e_y, e_width, e_height, color=outcome_color,
                        text=u"Asymetria \n lub \n brak asymetrii \n dla pojedynczego nagrania",
                        text_fontsize=20,
                        fill=True)

    return row_number + 1


picture_set = "/home/tmp/pp/*.png"
picture_set = "/x/tmp/pp/*.png"
picture_set = "/x/tmp/pp2/*.png"
png_files = glob.glob(picture_set)
png_files = sorted(png_files)

positions = [2,  # 2 hours in milis
             6.5,  # 6 hours, 30 minutes in milis
             11.5,  # 11 hours in milis
             16,  # 16 hours in milis
             20.5,  # 20 hours, 30 minutes in milis
             ]


def draw_simple_arrow(ax, posA=None, posB=None, path=None, tail_width=5, head_width=None, head_length=10,
                      color="black", label="", text=None, text_fontsize=14, x_text_pos=None, y_text_pos=None,
                      text_color="black", fill=False, lw=3.0):
    arrow_down = mpatches.FancyArrowPatch(posA=posA, posB=posB, path=path, color=color, label=label, lw=lw)
    arrow_down.set_fill(fill)
    if head_width == None and not tail_width == None:
        head_width = 3 * tail_width
    arrowstyle = mpatches.ArrowStyle.Simple(head_length=head_length, head_width=head_width, tail_width=tail_width)
    arrow_down.set_arrowstyle(arrowstyle)
    ax.add_patch(arrow_down)
    if not text == None:
        # when x is the same
        if x_text_pos == None and posA[0] == posB[0]:
            x_text_pos = posA[0]
        if y_text_pos == None and posA[0] == posB[0]:
            y_text_pos = posB[1] + abs((posA[1] - posB[1])) / 2.0

        # when y is the same
        if x_text_pos == None and posA[1] == posB[1]:
            x_text_pos = posA[0] + abs((posA[0] - posB[0])) / 2.0
        if y_text_pos == None and posA[1] == posB[1]:
            y_text_pos = posA[1]

        alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}

        font_1 = font_0.copy()
        font_1.set_size(text_fontsize)
        font_1.set_weight('bold')

        ax.text(x_text_pos, y_text_pos, text,
                # fontsize=text_fontsize,
                color=text_color,
                fontproperties=font_1,
                **alignment)


def create_24_tachogram(gs1, row_number, timing, des1,
                        slice_color="black"):

    max_timing = np.max(timing)

    ax_24_tachogram = plt.subplot(gs1[row_number, :])
    ax_24_tachogram.set_color_cycle(['blue'])
    ax_24_tachogram.plot(timing, des1)
    ax_24_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_24_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing) + 1, 1))
    ax_24_tachogram.set_xlim(0, max_timing)

    font_1 = font_0.copy()
    font_1.set_size('13')
    font_1.set_weight('bold')

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}

    y_lim_min = ax_24_tachogram.get_ylim()[0]
    y_lim_max = ax_24_tachogram.get_ylim()[1]
    shift = 50
    for position in positions:
        codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
        start_pos = position - 0.5
        stop_pos = position + 0.5
        vertices = [(start_pos, y_lim_max - shift),
                    (stop_pos, y_lim_max - shift),
                    (stop_pos, y_lim_min + shift),
                    (start_pos, y_lim_min + shift), (0, 0)]
        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='None', edgecolor=slice_color, zorder=3, lw=3)
        pathpatch.set_fill(False)
        ax_24_tachogram.add_patch(pathpatch)

        ax_24_tachogram.text(position, y_lim_min + 2 * shift, u"5 min.", fontproperties=font_1,
                             **alignment)  # size=15)

    leg = ax_24_tachogram.legend(['$\mathbf{%s}$' % ("RR")], loc='upper left')
    # change legend font properties
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')

    ax_24_tachogram.set_xlabel(u"Czas [godziny]", fontproperties=font_1)
    ax_24_tachogram.set_ylabel(u"RR [ms]", fontproperties=font_1)

    tachogram_label_pos = 18
    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')
    ax_24_tachogram.text(0.85, 0.9, u"Tachogram - 24 godziny", fontproperties=font_1, transform=ax_24_tachogram.transAxes)  # size=15)

    arrow_size = 4.5
    head_width = 45
    tail_width = 25
    head_length = 40
    arrow_shift = 100
    pos_start = positions[2] + 0.75
    pos_stop = positions[3] - 0.75
    draw_simple_arrow(ax_24_tachogram,
                      # posA=(pos_x - arrow_size / 2.0, y_lim_max - head_width - arrow_shift),
                      # posB=(pos_x + arrow_size / 2.0, y_lim_max - head_width - arrow_shift),
                      posA=(pos_start, y_lim_max - head_width - arrow_shift),
                      posB=(pos_stop, y_lim_max - head_width - arrow_shift),
                      tail_width=tail_width, head_width=head_width,
                      head_length=head_length, color="red",
                      text=u"Kierunek przesuwania okna",
                      text_fontsize=12,
                      lw=2.0,
                      )

    # ax_24_tachogram.text(tachogram_label_pos, y_lim - 200,
    #                  u"Tachogram - 24 godziny", fontproperties = font_1)
    bold_ticks_labels(ax_24_tachogram, fontsize=13)

    return row_number + 1


def create_empty_plot(gs1, row_number, ret_plot=False, ylim=20):
    # empty plot
    empty_plot = plt.subplot(gs1[row_number, :])
    empty_plot.set_ylim(0, ylim)
    # empty_plot.set_xlim(0, max_timing)
    empty_plot.grid(False)
    empty_plot.set_frame_on(False)
    empty_plot.title.set_visible(False)
    empty_plot.xaxis.set_major_locator(plt.NullLocator())
    empty_plot.yaxis.set_major_locator(plt.NullLocator())
    for tl in empty_plot.get_xticklabels():
        tl.set_visible(False)
    for tl in empty_plot.get_yticklabels():
        tl.set_visible(False)
    if ret_plot:
        return row_number + 1, empty_plot
    else:
        return row_number + 1


def create_poincare_windows_label(gs1, row_number):
    (_, label_plot) = create_empty_plot(gs1, row_number, ret_plot=True, ylim=3)

    #set_border(label_plot)
    #plt.setp(label_plot, frame_on=True)

    font_1 = font_0.copy()
    font_1.set_size('18')
    font_1.set_weight('bold')

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'bottom'}

    label_plot.text(0.5, 0.5, u"Chwilowe 5-minutowe wykresy mini-Poincaré", fontproperties=font_1, **alignment)

    #label_plot.set_title(u"Chwilowe 5-minutowe wykresy mini-Poincaré", fontproperties=font_1, **alignment)
    return row_number + 1


def create_poincare_windows_plot(gs1, row_number, timing, max_idx):

    for num, png_file in enumerate(png_files):

        ax_poincare_plot_png = plt.subplot(gs1[row_number, num])
        poincare_plot_png = mpimg.imread(png_file)
        ax_poincare_plot_png.imshow(poincare_plot_png)  # , aspect='auto') #, origin='lower')
        ax_poincare_plot_png.set_axis_off()
        ax_poincare_plot_png.set_frame_on(False)
        # ax_poincare_plot_png.autoscale_view(tight=True)

        plt.setp(ax_poincare_plot_png, frame_on=True)

#         alignment = {'horizontalalignment':'left', 'verticalalignment':'center'}
#         text_fontsize = 20
#         font_1 = font_0.copy()
#         font_1.set_size(text_fontsize)
#         font_1.set_weight('bold')
#         ax_ekg.text(0.1, 0.1, u"EKG", fontproperties=font_1, **alignment)
    return row_number + 1


def create_arrows_plot(gs1, row_number, timing, max_idx=None):

    position_labels = ["G: 02 \n M: 00 \n S: 00",
                       "G: 06 \n M: 30 \n S: 00",
                       "G: 11 \n M: 30 \n S: 00",
                       "G: 16 \n M: 00 \n S: 00",
                       "G: 20 \n M: 30 \n S: 00",
                       ]
    max_timing = np.max(timing)

    ax_arrow_plot = plt.subplot(gs1[row_number, :])
    ax_arrow_plot.set_axis_off()
    ax_arrow_plot.set_frame_on(False)
    ax_arrow_plot.set_xlim(0, max_timing)

    alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
    text_fontsize = 12

    for idx, pos_x in enumerate(positions):
        tail_width = 80
        head_width = tail_width + 30
        head_length = 30
        draw_simple_arrow(ax_arrow_plot, posA=(pos_x, 1.0), posB=(pos_x, 0.4),
                          tail_width=tail_width, head_width=head_width,
                          head_length=head_length, color="green",
                          text=position_labels[idx],
                          text_fontsize=text_fontsize,
                          )

    line = Line2D(range(1), range(1), linestyle='None', marker='None', color="blue")
    labels = 'G - godzina\n M - minuta \nS - sekunda'
    leg = ax_arrow_plot.legend([line], [labels], loc='upper right')
    plt.setp(leg.get_texts(), fontsize='large')
    plt.setp(leg.get_texts(), fontweight='bold')
    ax_arrow_plot.add_artist(leg)

    return row_number + 1


def create_data_plot(gs1, row_number, timing, max_idx=None):

    data = [
        {'SD1_d': '20,21', 'SD1_a': '14,57', 'SD2_d': '72,21',
         'SD2_a': '81,65', 'SDNN_d': '\,53,02',  'SDNN_a': '\,58,65'},
        {'SD1_d': '20,71', 'SD1_a': '15,62', 'SD2_d': '52,85',
         'SD2_a': '70,90', 'SDNN_d': ' 40,14',  'SDNN_a': ' 51,34'},
        {'SD1_d': '16,70', 'SD1_a': '13,09', 'SD2_d': '80,15',
         'SD2_a': '39,35', 'SDNN_d': ' 57,89',  'SDNN_a': ' 63,85'},
        {'SD1_d': '24,07', 'SD1_a': '24,29', 'SD2_d': '48,60',
         'SD2_a': '41,79', 'SDNN_d': '38,34',  'SDNN_a': '34,18'},
        {'SD1_d': '23,36', 'SD1_a': '20,77', 'SD2_d': '54,89',
         'SD2_a': '59,10', 'SDNN_d': '42,18',  'SDNN_a': '44,30'},
    ]

    labels = ['SD1_d', 'SD2_d', 'SDNN_d', 'SD1_a', 'SD2_a', 'SDNN_a']

    def get_math_label(data_item):
        item_labels1 = ";\,".join(["{}={}".format(
            label, data_item[label]) for label in labels[:3]]
        )
        item_labels2 = ";\,".join(["{}={}".format(
            label, data_item[label]) for label in labels[3:]]
        )

        #item_labels1 = ",\,".join([label for label in labels])
        #item_labels2 = ",\,".join([data_item[label] for label in labels])
        return "$\mathbf{" + item_labels1 + "}$\n$\mathbf{" + item_labels2 + "}$"

    position_labels = [get_math_label(data_item) for data_item in data]
    max_timing = np.max(timing)

    ax_data_plot = plt.subplot(gs1[row_number, :])
    ax_data_plot.set_axis_off()
    ax_data_plot.set_frame_on(False)
    p_height = 0.9
    b_height = p_height - 0.1

    ax_data_plot.set_xlim(0, max_timing)
    ax_data_plot.set_ylim(0, p_height)
    ax_data_plot.grid(False)
    ax_data_plot.title.set_visible(False)

    #alignment = {'horizontalalignment': 'center', 'verticalalignment': 'center'}
    #text_fontsize = 12

    positions = [2,  # 2 hours in milis
             6.6,  # 6 hours, 30 minutes in milis
             11.3,  # 11 hours in milis
             15.9,  # 16 hours in milis
             20.5,  # 20 hours, 30 minutes in milis
             ]

    b_width = 3.3
    y = p_height
    text_fontsize = 13
    for idx, pos_x in enumerate(positions):
        draw_box_with_text(ax_data_plot,
                           pos_x-1.3, y,
                           b_width, b_height,
                           position_labels[idx],
                           text_fontsize=text_fontsize,
                           linewidth=0,
                           #linestyle='dotted'
                           #edgecolor='None'
                           #text_fontsize=5,
                           #txt,
                           #color='black',
                           #text_color='red'
                           )

    return row_number + 1


def initialize_figure(start_hour, stop_hour):
    # f = plt.figure(figsize=(70, 20))
    # f = plt.figure(figsize=(40, 15))
    # proc = 10 / 100.0
    # f = plt.figure(figsize=(40-40*proc, 15-15*proc))
    f = plt.figure(figsize=(26, 15))

    font_1 = font_0.copy()
    font_1.set_size('20')
    font_1.set_weight('bold')
    plt.suptitle(u"Dynamika zmian asymetrii rytmu serca w wykresach mini-Poincaré w 24-godzinnym nagraniu",
                 fontproperties=font_1, y=0.995, fontsize=25)

    empty_ratio = 0.2
    height_ratios = [empty_ratio,
                     3-2.5*empty_ratio,  # 1 24-tachogram
                     1.5*empty_ratio,
                     0.8,  # 2 arrows
                     #0.1, # label for poincare windows
                     0.1, # label for poincare windows
                     #3,  # 3 poincare plot windows
                     2.5,  # 3 poincare plot windows
                     0.001,  # empty plot
                     0.499,  # data row
                     ]

    num_rows = len(height_ratios)

    num_cols = len(png_files)
    width_ratios = [1] * num_cols

    row_number = 0

    gs1 = GridSpec(num_rows, num_cols, height_ratios=height_ratios, width_ratios=width_ratios)
    gs1.update(left=0.04, right=0.99, wspace=0.0, hspace=0.0, bottom=0.04, top=0.98)
    return f, gs1


start_hour = None
start_hour = 11
stop_hour = 13
if start_hour == None:
    max_idx = 23
else:
    max_idx = 24
row_number = 0
window_step = 1  # 1 hour
sym_indexes = [1, 5, 6, 12, 21]  # only multiple of window_step are allowed

(f, gs1) = initialize_figure(start_hour, stop_hour)

(des1, timing, timing_0) = get_24h_data()

# 1
row_number = create_empty_plot(gs1, row_number)

row_number = create_24_tachogram(gs1, row_number, timing, des1, slice_color="red")

row_number = create_empty_plot(gs1, row_number)

row_number = create_arrows_plot(gs1, row_number, timing, max_idx)

row_number = create_poincare_windows_label(gs1, row_number)

row_number = create_poincare_windows_plot(gs1, row_number, timing, max_idx)

row_number = create_empty_plot(gs1, row_number)

row_number = create_data_plot(gs1, row_number, timing, max_idx)
# #2
# row_number = create_zoom_plot(gs1, row_number, timing,
#                                start_hour=start_hour, stop_hour=stop_hour)
#
# (des1, timing) = get_5m_data(des1, timing_0, start_hour, stop_hour)
#
# #3
# row_number = create_simple_tachogram(gs1, row_number, timing, des1,
#                             start_hour=start_hour, stop_hour=stop_hour)
#
# #4
# row_number = create_empty_plot(gs1, row_number)
#
# #5
# row_number = create_arrow_plot_5m(gs1, row_number, timing, max_idx)
#
# #6
# #row_number = create_empty_plot(gs1, row_number)
#
# #7
# row_number = create_windowed_tachogram(gs1, row_number, timing, des1,
#                     max_idx, start_hour=start_hour, stop_hour=stop_hour)
#
# #8
# row_number = create_empty_plot(gs1, row_number)
#
# #9
# row_number = create_descriptors_arrow(gs1, row_number)
#
# #10
# row_number = create_empty_plot(gs1, row_number)
#
# #11
# row_number = create_windowed_descriptors_tachogram(gs1, row_number, timing, des1, max_idx,
#                         sym_indexes=sym_indexes, start_hour=start_hour, stop_hour=stop_hour)
#
# #12
# row_number = create_shapes_plot(gs1, row_number, timing, max_idx, sym_indexes=sym_indexes)

#plt.tight_layout()
if save_fig:
    file_ = "/tmp/poincare_plots_5_min.png"
    plt.savefig(file_, bbox_inches='tight', pad_inches=0.1)
    #plt.savefig(file_)
    print('Save into ', file_)
else:
    plt.show()

