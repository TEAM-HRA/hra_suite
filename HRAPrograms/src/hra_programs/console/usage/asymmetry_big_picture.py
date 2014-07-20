#!/usr/bin/env python
#-*- coding:utf-8 -*-
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


from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches


def make_ticklabels_invisible(fig):
    return
    for i, ax in enumerate(fig.axes):
        #ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)



# demo 3 : gridspec with subplotpars set.

f = plt.figure()

max_idx = 23

def can_show(show_rows, idx):
    return True if idx < len(show_rows) and show_rows[idx] else False


show_rows = [True, True, True, True, True]
#show_rows = [False, True, False, False, False]
all_ratios = [3, 0.3, 3, 0.5, 4]
height_ratios = [all_ratios[idx] for idx, s in enumerate(show_rows) if s == True]
num_rows = len([s for s in show_rows if s == True])
num_cols = 2

row_number = 0

#plt.suptitle("GirdSpec w/ different subplotpars")
#plt.suptitle("Schemat nowego dynamicznego podejscia w analizie asymetrii rytmu serca wykorzystujacego okno danych.")

gs1 = GridSpec(num_rows, num_cols, height_ratios=height_ratios) #[3, 0.3, 3, 0.5, 4])
#gs1.update(left=0.05, right=0.48, wspace=0.05)
gs1.update(left=0.04, right=0.99, wspace=0.1, hspace=0.2, bottom=0.04, top=0.98)

if can_show(show_rows, 0):
    ax_ekg = plt.subplot(gs1[row_number, :])
    ekg_img = mpimg.imread('/home/jurek/git_repos/doctorate/Doktorat/graph/ekg.png')
    ax_ekg.imshow(ekg_img) #, aspect='auto') #, origin='lower')
    ax_ekg.set_axis_off()
    ax_ekg.set_frame_on(False)
    ax_ekg.autoscale_view(tight=True)
    #ax_ekg.set_title("EKG")
    ax_ekg.text(0.1, 0.1, "EKG", va="center", ha="left", size=20)
    row_number = row_number + 1

if can_show(show_rows, 1):
    ax_arrow_down = plt.subplot(gs1[row_number, :])
    patches = []
    arrow_down = mpatches.Arrow(0.5, 1, -0, -0.9, width=0.05, color="grey", label="Dane z EKG")
    arrow_down.set_fill(True)
    patches.append(arrow_down)
    collection = PatchCollection(patches,  alpha=0.3) #cmap=plt.cm.hsv,)
    ax_arrow_down.set_axis_off()
    ax_arrow_down.set_frame_on(False)
    #ax_arrow_down.autoscale_view(tight=True)
    ax_arrow_down.add_patch(arrow_down)
    row_number = row_number + 1


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

if can_show(show_rows, 2):
    ax_tachogram = plt.subplot(gs1[row_number, :])
    ax_tachogram.set_color_cycle(['blue'])
    ax_tachogram.plot(timing, des1)
    ax_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_tachogram.set_xlim(0, max_timing)
    ax_tachogram.legend(['$\mathbf{%s}$' % ("RR"),], loc='upper left')
    ax_tachogram.set_xlabel(r'\large{Czas [godziny]}')
    ax_tachogram.set_ylabel(r'\large{Wartość [ms]}')
    #ax_tachogram.set_text(0.8, 0.8, 'Tachogram')
    ax_tachogram.text(max_idx - max_idx / 11.8, des1_max - des1_max / 70,
                      "Tachogram", size=20)
    #print('Title: ' + str(ax_tachogram.get_title()))
    #ax_tachogram.set_title(None)
    row_number = row_number + 1


#arrow = mpatches.Arrow(grid[5, 0]-0.05, grid[5, 1]-0.05, 0.1, 0.1, width=0.1)

if can_show(show_rows, 3):
    arrow_left = mpatches.Arrow(0.9, 1.1, -0.05, -1, width=0.15, color="black", label="Analiza")
    arrow_left.set_fill(True)
    #patches = []
    #patches.append(arrow_left)
    #collection = PatchCollection(patches,  alpha=0.3) #cmap=plt.cm.hsv,)
    #colors = np.linspace(0, 1, len(patches))
    #collection.set_array(np.array(colors))
    ax_arrow_left = plt.subplot(gs1[row_number,0])
    ax_arrow_left.text(0.5, 0.5, "Standardowa analiza HRA całego nagrania" , va="center", ha="center", size=20)
    ax_arrow_left.set_axis_off()
    ax_arrow_left.set_frame_on(False)
    #ax_arrow_left.autoscale_view(tight=True)
    #ax_arrow_left.add_collection(collection)
    ax_arrow_left.add_patch(arrow_left)


    arrow_right = mpatches.Arrow(0.1, 1.1, 0.05, -1, width=0.15, color="green")
    arrow_right.set_fill(True)
    ax_arrow_right = plt.subplot(gs1[row_number,1])
    ax_arrow_right.text(0.5, 0.5, "Nowa analiza HRA przy pomocy okna danych",
                         va="center", ha="center", color="green",  size=20)
    ax_arrow_right.set_axis_off()
    ax_arrow_right.set_frame_on(False)
    #ax_arrow_right.autoscale_view(tight=True)
    #ax_arrow_left.add_collection(collection)
    ax_arrow_right.add_patch(arrow_right)
    row_number = row_number + 1

if can_show(show_rows, 4):
    # LEFT TACHOGRAM START
    ax_left_tachogram = plt.subplot(gs1[row_number,0])
    ax_left_tachogram.set_color_cycle(['blue', 'red'])
    ax_left_tachogram.plot(timing, des1)
    ax_left_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_left_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_left_tachogram.set_xlim(0, max_timing)
    #ax_left_tachogram.legend(['Tachogram'], loc='upper right')
    ax_left_tachogram.set_xlabel(r'\large{Czas [godziny]}')
    ax_left_tachogram.set_ylabel(r'\large{Wartość [ms]}')
    ax_left_tachogram.text(max_idx - max_idx / 7, des1_max - des1_max / 70,
                      "Tachogram", size=20)
    #ax_left_tachogram.set_title("Tachogram")



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
    ax_left_tachogram.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 24 godziny"], loc='upper left')
    # LEFT TACHOGRAM STOP

    # RIGHT TACHOGRAM START
    ax_right_tachogram = plt.subplot(gs1[row_number,1])
    ax_right_tachogram.set_color_cycle(['blue', 'red'])
    ax_right_tachogram.plot(timing, des1)
    ax_right_tachogram.ticklabel_format(style='sci', axis='x', scilimits=(0, max_timing))
    ax_right_tachogram.xaxis.set_ticks(np.arange(0, int(max_timing)+1, 1))
    ax_right_tachogram.set_xlim(0, max_timing)
    ax_right_tachogram.set_xlabel(r'\large{Czas [godziny]}')
    ax_right_tachogram.set_ylabel(r'\large{Wartość [ms]}')
    ax_right_tachogram.text(max_idx - max_idx / 7, des1_max - des1_max / 70,
                      "Tachogram", size=20)

    max_idx = 23
    #ax_right_tachogram.legend(numpoints=10)


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
    ax_right_tachogram.legend(['$\mathbf{%s}$' % ("RR"), "Okno danych - 5 minut"], loc='upper left', numpoints=5)


    arrow_size = 4
    arrow_window_right = mpatches.Arrow(max_idx / 2 - arrow_size / 2,
                                        des1_max - des1_max / 35,
                                        4, 0,
                                        width=100, color="red") #, zorder=3)
    arrow_window_right.set_fill(True)
    ax_right_tachogram.add_patch(arrow_window_right)
    row_number = row_number + 1

#ax_right_tachogram.axis('equal')
#ax_right_tachogram.axis('scaled')
#ax_right_tachogram.dataLim.update_from_data_xy(vertices)
#ax_right_tachogram.autoscale_view()
# RIGHT TACHOGRAM STOP


#ax4 = plt.subplot(gs1[-1, :-1])
#ax5 = plt.subplot(gs1[-1, -1])

#gs2 = GridSpec(3, 3)
#gs2.update(left=0.55, right=0.98, hspace=0.05)
#ax4 = plt.subplot(gs2[:, :-1])
#ax5 = plt.subplot(gs2[:-1, -1])
#ax6 = plt.subplot(gs2[-1, -1])

make_ticklabels_invisible(plt.gcf())

plt.show()

