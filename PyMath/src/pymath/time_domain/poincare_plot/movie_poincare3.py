#!/usr/bin/python
#
import os                         # For issuing commands to the OS.
import sys                        # For determining the Python version.
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from matplotlib import rcParams
import cStringIO
from matplotlib.patches import Rectangle
#from matplotlib import legend
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerLine2D


def get_time_label_for_miliseconds(miliseconds):
    hours, remainder = divmod(miliseconds / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    return 'h:%02d, m:%02d, s:%02d' % (hours, minutes, seconds)


def get_max_index_for_cumulative_sum_greater_then_value(_array, value,
                                                     start_index=0):
    """
    this function returns the first index of _array calculated from
    cumulative sum of values of _array where cumulative sum value is >= then
    passed value; searched indexes starts at start_index position
    """
    indexes = range(start_index, len(_array))
    sub_array = _array.take(indexes)
    cumulative_array = pl.cumsum(sub_array)
    indexes = pl.where(cumulative_array >= value)[0]
    return indexes[0] + start_index if len(indexes) > 0 else -1


#
# Now that we have an example data set (x,y) to work with, we can
# start graphing it and saving the images.
#
s_index = 1
#filename = "/home/jurek/volumes/doctoral/dane/24h/part1/ANDRZ29.rea"
filename = "/home/jurek/tmp/movie_poincare.rea"
signal = pl.loadtxt(filename, skiprows=1, usecols=[s_index], unpack=True)
signal = signal[signal < 2000]

signal_plus = signal.take(pl.arange(0, len(signal) - 1))
signal_minus = signal.take(pl.arange(1, len(signal)))

count = 3000
step = 100
show_plot_legends = False

sample = pl.arange(0, sum(signal), step)
cumsum = pl.cumsum(signal)
size = step * count

_sum = pl.sum(signal)
_max = pl.amax(signal)
_min = pl.amin(signal)
_mean = pl.mean(signal)
_median = pl.median(signal)

#fig = plt.figure()
#l, = plt.plot([], [], 'bo')

margin = 50

#plt.xlim(_min - margin, _max + margin)
#plt.ylim(_min - margin, _max + margin)

fig = plt.figure()
#fig.suptitle('Animacja wykresow Poincare', fontsize=14, fontweight='bold')
ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
ax.axis([_min - margin, _max + margin,
         _min - margin, _max + margin])
#ax.legend(('Legend'), 'upper right', shadow=True)
skip_frames = 0 #10000
signal_size = len(signal)
#signal_size = 100
#signal_size = 10000
#signal_size = 10
#signal_size = 10000
output_dir = "/ramdisk/tmp_" + str(signal_size) + "/"
output_dir = "/home/tmp/tmp/"
active_color = np.array([255, 0, 0]) / 255
#active_color = np.array([255, 78, 247]) / 255
#active_color = np.array([255, 50, 50]) / 255
#active_color = '#FFF785'
inactive_color = np.array([0, 0, 0]) / 255
centroid_color = np.array([0, 255, 0]) / 255
old_signal0_plus = None
x_data = None
y_data = None
rams = []
active_size = 20
inactive_size = 10
centroid_size = 40
fps = 30
#fps = 700
dpi = 100
for i in range(signal_size):  # range(len(y)):

    #rcParams['legend.numpoints'] = 1
    _save = True
    filename = output_dir + str('%06d' % i) + '.png'
    ax.axis([_min - margin, _max + margin,
             _min - margin, _max + margin])
    ax.set_xlabel('$RR_{n}$ [ms]')
    ax.set_ylabel('$RR_{n+1}$ [ms]')
    #ax.set_adjustable('box')
    #ax.legend((filename), 'upper right', shadow=True)

    rr_start = i
    rr_stop = get_max_index_for_cumulative_sum_greater_then_value(signal,
                                                                  size, i)
    if rr_stop == -1:
        break
    indexes = pl.arange(rr_start, rr_stop)

    signal0 = signal.take(indexes)

    indexes_plus = pl.arange(0, len(signal0) - 1)
    signal0_plus = signal0.take(indexes_plus)

    indexes_minus = pl.arange(1, len(signal0))
    signal0_minus = signal0.take(indexes_minus)

    mean_plus = pl.mean(signal0_plus)
    mean_minus = pl.mean(signal0_minus)

    if x_data == None:
        time_label = get_time_label_for_miliseconds(0)
    else:
        time_label = get_time_label_for_miliseconds(np.sum(x_data))
    #p = Rectangle((0, 0), 1, 1, fc="r")
    p = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none',
                  linewidth=0)
    #p = Rectangle((0, 0), 0, 0)
    leg_time = ax.legend([p], [time_label], 'upper left')
    leg_time.get_frame().set_alpha(0.5)
    ltext = leg_time.get_texts()
    plt.setp(ltext, fontsize=8)
    if show_plot_legends:
        ax.add_artist(leg_time)

    s_plus = len(signal0_plus)
    if x_data == None:
        x_data = signal0_plus.copy()
        y_data = signal0_minus.copy()

        a_plot = ax.scatter(x_data, y_data, c=active_color, s=active_size)
        c_plot = ax.scatter([mean_plus], [mean_minus], s=centroid_size,
                            c=centroid_color) # @IgnorePep8        

        if show_plot_legends:
            leg_plots = ax.legend((a_plot, c_plot), ('biezacy PP', "controid"),
                            'upper right', scatterpoints=1)  # , shadow=True)
            leg_plots.get_frame().set_alpha(0.5)
    else:
        old_s_plus = len(old_signal0_plus)
        ok = False

        if s_plus >= old_s_plus:
            for idx in xrange(1, old_s_plus):
                if np.all(old_signal0_plus[idx:] \
                            == signal0_plus[idx - 1: old_s_plus - idx]):
                    x_data = np.hstack((x_data,
                                        signal0_plus[old_s_plus - idx:]))
                    y_data = np.hstack((y_data,
                                        signal0_minus[old_s_plus - idx:]))
                    max_inactive_idx = len(x_data) - s_plus
                    i_plot = ax.scatter(x_data[:max_inactive_idx],
                                        y_data[:max_inactive_idx],
                                        s=inactive_size, c=inactive_color)
                    a_plot = ax.scatter(x_data[max_inactive_idx:],
                                        y_data[max_inactive_idx:],
                                        s=active_size, c=active_color)
                    c_plot = ax.scatter([mean_plus], [mean_minus],
                                        s=centroid_size,
                                        c=centroid_color)
                    ok = True
                    break
        else:
            for idx in xrange(1, old_s_plus):
                if idx + s_plus <= old_s_plus \
                    and np.all(old_signal0_plus[idx:idx + s_plus] \
                                == signal0_plus):
                    max_inactive_idx = len(x_data) - old_s_plus + idx
                    ax.scatter(x_data[:max_inactive_idx],
                               y_data[:max_inactive_idx],
                               s=inactive_size, c=inactive_color)
                    i_plot = ax.scatter(x_data[max_inactive_idx + s_plus:],
                                        y_data[max_inactive_idx + s_plus:],
                                        s=inactive_size, c=inactive_color)
                    a_plot = ax.scatter(
                            x_data[max_inactive_idx:max_inactive_idx + s_plus],
                            y_data[max_inactive_idx:max_inactive_idx + s_plus],
                            s=active_size, c=active_color)
                    c_plot = ax.scatter([mean_plus], [mean_minus],
                                        s=centroid_size, c=centroid_color)
                    ok = True
                    #_save = False
                    break
        if ok == False:
            print('s_plus: ' + str(s_plus) + ' old_s_plus: ' + str(old_s_plus)) # @IgnorePep8
            print('old_signal0_plus: ' + str(old_signal0_plus))
            print('signal0_plus:     ' + str(signal0_plus))
            raise Exception('Error for ' + str(i))

        if show_plot_legends:
            leg_plots = ax.legend((a_plot, i_plot, c_plot),
                   ('biezacy PP', "poprzednie PP", "controid"),
                   'upper right', scatterpoints=1)  # , shadow=True)
            leg_plots.get_frame().set_alpha(0.5)
            ltext = leg_plots.get_texts()
            plt.setp(ltext, fontsize=8)
    old_signal0_plus = signal0_plus

    #ax.legend((a_plot), (str('#% 6d' % i)), 'upper left', shadow=True)
    #
    # Notice the use of LaTeX-like markup.
    #
    #title(r'$\cal{N}(\mu, \sigma^2)$', fontsize=20)

    #ram = cStringIO.StringIO()
    #fig.savefig(ram, format='raw', dpi=100)
    #ram.close()
    #rams.append(ram)

    if i < skip_frames:
        print 'Skipped file', filename, " [", i, " /", signal_size, "]"
    else:

        #_save = False
        #filename = str('%06d' % i) + '.png'
        if _save:
            savefig(filename, dpi=dpi)
        #fig.clf()

        #plt.draw()
        #fig.clf()
        #
        # Let the user know what's happening.
        #
        print 'Wrote file', filename, " [", i, " /", signal_size, "]"

    #
    # Clear the figure to make way for the next image.
    #
    plt.cla()


output_movie_file = 'output_' + str(signal_size) + '.avi'
command = ('mencoder',
           'mf://' + output_dir + '*.png',
           '-mf',
           #'type=png:w=1024:h=800:fps=30',
           'type=png:w=1024:h=1024:fps=' + str(fps),
           '-ovc',
           'lavc',
           '-lavcopts',
           'vcodec=mpeg4',
           '-oac',
           'copy',
           '-o',
           output_movie_file)

os.spawnvp(os.P_WAIT, 'mencoder', command)

#command = ('rm ', '*.png')
#os.spawnvp(os.P_WAIT, 'mencoder', command)

#mencoder mf://*.png -mf type=png:w=1024:h=800:fps=30 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output.avi
#mencoder mf:///home/tmp/tmp/*.png -mf type=png:w=1024:h=1024:fps=30 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output_test.avi

#mencoder mf://*.png -mf type=png:w=1024:h=800:fps=30 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output.avi

#bin=StringIO()
#bin.write("/x5F/x5F%c" % 0xFF)

#file = open ("my.bin","wb")
#file.write(bin.getvalue())
#file.close()
