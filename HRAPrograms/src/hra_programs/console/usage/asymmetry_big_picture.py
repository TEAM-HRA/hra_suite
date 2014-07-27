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
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties

font_0 = FontProperties('DejaVu Sans')

#pl.rc('text', usetex=True)
#pl.rc('text.latex',unicode=True)

# preamble = [
#             '\usepackage[polish]{babel}',
#             #'\usepackage[utf8]{inputenc}',
#             #'\usepackage[T1]{polski}'
#             ]
#pylab.rc('text.latex',preamble=preamble)
#pl.rc('text.latex',preamble='\usepackage[T1]{polski}') # oryg
#pylab.rc('text.latex',preamble='\usepackage[T1]{fontenc}')
#pylab.rc('text.latex',preamble='\usepackage{polski}')
#pl.rcParams['text.latex.preamble'] = [r'\boldmath']


from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches


def create_empty_plot(gs):
    # empty plot
    empty_plot = plt.subplot(gs)
    empty_plot.grid(False)
    empty_plot.set_frame_on(False)
    empty_plot.title.set_visible(False)
    empty_plot.xaxis.set_major_locator(plt.NullLocator())
    empty_plot.yaxis.set_major_locator(plt.NullLocator())
    for tl in empty_plot.get_xticklabels():
        tl.set_visible(False)
    for tl in empty_plot.get_yticklabels():
        tl.set_visible(False)


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

# def make_ticklabels_invisible(fig):
#     return
#     for i, ax in enumerate(fig.axes):
#         #ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
#         for tl in ax.get_xticklabels() + ax.get_yticklabels():
#             tl.set_visible(False)

f = plt.figure()

max_idx = 23

gs0 = GridSpec(3, 1, height_ratios=[3.0, 0.5, 6.5])
gs0.update(left=0.04, right=0.99, wspace=0.01, hspace=0.0, bottom=0.05, top=0.98)

gs00 = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs0[0],
                                        width_ratios=[1.5, 0.3, 0.35, 7.85],
                                        wspace=0.0, hspace=0.0)

##############################################
##
## first subgrid
##
##############################################

# EKG Axis
ax_ekg = plt.subplot(gs00[0, 0])
ekg_img = mpimg.imread('/home/jurek/git_repos/doctorate/Doktorat/graph/ekg.png')
ax_ekg.imshow(ekg_img) #, aspect='auto') #, origin='lower')
ax_ekg.set_axis_off()
ax_ekg.set_frame_on(False)
ax_ekg.autoscale_view(tight=True)

alignment = {'horizontalalignment':'left', 'verticalalignment':'center'}
text_fontsize = 20
font_1 = font_0.copy()
font_1.set_size(text_fontsize)
font_1.set_weight('bold')
ax_ekg.text(0.1, 0.1, u"EKG", fontproperties=font_1, **alignment)

####################################
ax_arrow_left = plt.subplot(gs00[0, 1])
ax_arrow_left.set_axis_off()
ax_arrow_left.set_frame_on(False)

arrow_left = mpatches.Arrow(0.0, 0.5, 0.9, 0.0, width=0.25, color="black", lw=4) #, label="Dane z EKG")
arrow_left.set_fill(False)
ax_arrow_left.add_patch(arrow_left)

#empty plot
create_empty_plot(gs00[0,2])

###################################
file_rr = "/home/jurek/volumes/doctoral/dane/long_corrected/jakubas_RR_P.rea"
usecols = (1, 2,)
des1, annotation = np.loadtxt(file_rr, usecols=usecols, skiprows=1, unpack=True)

#odfiltrowanie adnotacji
if (len(pl.array(pl.find(annotation != 0)) > 0)):
    des1 = des1[pl.array(pl.find(annotation == 0))]

timing = np.cumsum(des1)
timing = timing / 3600000
des1_max = np.max(des1)
des1_min = np.min(des1)
max_timing = np.max(timing)


#################################
ax_tachogram = plt.subplot(gs00[0, 3])
ax_tachogram.set_color_cycle(['blue'])
ax_tachogram.plot(timing, des1)
ax_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
ax_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing) + 1, 1))
ax_tachogram.set_xlim(0, max_timing)
leg = ax_tachogram.legend([u"$\mathbf{%s}$" % ("RR")], loc='upper left')
plt.setp(leg.get_texts(), fontsize='large')
plt.setp(leg.get_texts(), fontweight='bold')

font_1 = font_0.copy()
font_1.set_size('11')
font_1.set_weight('bold')
ax_tachogram.set_xlabel(u"Czas [godziny]", fontproperties=font_1)
ax_tachogram.set_ylabel(u"Wartość [ms]", fontproperties=font_1)
#ax_tachogram.set_text(0.8, 0.8, 'Tachogram')

tachogram_label_pos = 20
font_1 = font_0.copy()
font_1.set_size('18')
font_1.set_weight('bold')
ax_tachogram.text(max_idx - max_idx / 11.8, des1_max - des1_max / 70,
                  u"Tachogram", fontproperties=font_1)
bold_ticks_labels(ax_tachogram)

##############################################
##
## second subgrid
##
##############################################

gs_empty = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs0[1],
                                            wspace=0.0, hspace=0.0)
empty_arrow = plt.subplot(gs_empty[0, :])
create_empty_plot(gs_empty[0, :])


##############################################
##
## third subgrid
##
##############################################

gs01 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=gs0[2],
                                        height_ratios=[1, 9],
                                        width_ratios=[4.825, 0.35, 4.825],
                                        wspace=0.0, hspace=0.0)

#################################

ax_arrow = plt.subplot(gs01[0, :])
ax_arrow.set_axis_off()
ax_arrow.set_frame_on(False)

text_fontsize = 20
alignment = {'horizontalalignment':'center', 'verticalalignment':'center'}
font_1 = font_0.copy()
font_1.set_size(text_fontsize)
font_1.set_weight('bold')

ax_arrow.text(0.25, 0.5, u"Standardowa analiza HRA całego nagrania" ,
                   fontproperties=font_1, **alignment)

arrow_left = mpatches.Arrow(0.5, 1.1, -0.05, -1, width=0.07, color="black", label="Analiza")
arrow_left.set_fill(True)
ax_arrow.add_patch(arrow_left)

ax_arrow.text(0.75, 0.5, u"Nowa analiza HRA przy pomocy okna danych", color="green",
                    fontproperties=font_1, **alignment)

arrow_right = mpatches.Arrow(0.51, 1.1, 0.05, -1, width=0.07, color="green")
arrow_right.set_fill(True)
ax_arrow.add_patch(arrow_right)


#################################
# LEFT TACHOGRAM START
ax_left_tachogram = plt.subplot(gs01[1, 0])
ax_left_tachogram.set_color_cycle(['blue', 'red'])
ax_left_tachogram.plot(timing, des1)
ax_left_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
ax_left_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
ax_left_tachogram.set_xlim(0, max_timing)

font_1 = font_0.copy()
font_1.set_size('11')
font_1.set_weight('bold')

ax_left_tachogram.set_xlabel(u"Czas [godziny]", fontproperties=font_1)
ax_left_tachogram.set_ylabel(u"Wartość [ms]", fontproperties=font_1)

font_1 = font_0.copy()
font_1.set_size('20')
font_1.set_weight('bold')
ax_left_tachogram.text(max_idx - 4, des1_max - des1_max / 70,
                  u"Tachogram", fontproperties=font_1)
#ax_left_tachogram.set_title("Tachogram")

bold_ticks_labels(ax_left_tachogram)

vertices = []
codes = []
codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
vertices = [(0, des1_max - des1_max / 10),
            (max_idx, des1_max - des1_max / 10),
            (max_idx, des1_min + des1_max / 10),
            (0, des1_min + des1_max / 10), (0, 0)]
vertices = np.array(vertices, float)
path = Path(vertices, codes)
pathpatch = PathPatch(path, facecolor='None', edgecolor='red', zorder=3, lw=4)
ax_left_tachogram.add_patch(pathpatch)
leg  = ax_left_tachogram.legend([u"$\mathbf{%s}$" % ("RR"), u"Okno danych - 24 godziny"], loc='upper left')
plt.setp(leg.get_texts(), fontsize='large')
plt.setp(leg.get_texts(), fontweight='bold')
# LEFT TACHOGRAM STOP

#empty plot
create_empty_plot(gs01[1, 1])

# RIGHT TACHOGRAM START
ax_right_tachogram = plt.subplot(gs01[1, 2])
ax_right_tachogram.set_color_cycle(['blue', 'red'])
ax_right_tachogram.plot(timing, des1)
ax_right_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
ax_right_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
ax_right_tachogram.set_xlim(0, max_timing)

font_1 = font_0.copy()
font_1.set_size('11')
font_1.set_weight('bold')
ax_right_tachogram.set_xlabel(u"Czas [godziny]", fontproperties=font_1)
ax_right_tachogram.set_ylabel(u"Wartość [ms]", fontproperties=font_1)

font_1 = font_0.copy()
font_1.set_size('20')
font_1.set_weight('bold')
ax_right_tachogram.text(max_idx - 4, des1_max - des1_max / 70,
                  u"Tachogram", fontproperties=font_1)

first_lw = 0.5
lws = np.linspace(first_lw, 4, max_idx + 1 + first_lw)[::-1]


for idx, lw in zip(range(max_idx - 1, -1, -1), lws):
    vertices = []
    codes = []
    codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
    vertices = [(idx, des1_max - des1_max / 10),
                (idx + 1, des1_max - des1_max / 10),
                (idx + 1, des1_min + des1_max / 10),
                (idx, des1_min + des1_max / 10), (0, 0)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    pathpatch = PathPatch(path, facecolor='None', edgecolor='red', zorder=3, lw=lw)
    pathpatch.set_fill(False)
    ax_right_tachogram.add_patch(pathpatch)

leg = ax_right_tachogram.legend([u"$\mathbf{%s}$" % ("RR"), "Okno danych - 5 minut"],
                                 loc='upper left', numpoints=5)
plt.setp(leg.get_texts(), fontsize='large')
plt.setp(leg.get_texts(), fontweight='bold')

bold_ticks_labels(ax_right_tachogram)

arrow_size = 4
arrow_window_right = mpatches.Arrow(max_idx / 2 - arrow_size / 2,
                                    des1_max - des1_max / 35,
                                    4, 0,
                                    width=100, color="red") #, zorder=3)
arrow_window_right.set_fill(True)
ax_right_tachogram.add_patch(arrow_window_right)

plt.show()