#!/usr/bin/python
#
import os                         # For issuing commands to the OS.
import sys                        # For determining the Python version.
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import cStringIO


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
ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
ax.axis([_min - margin, _max + margin,
         _min - margin, _max + margin])
#ax.legend(('Legend'), 'upper right', shadow=True)

signal_size = len(signal)
signal_size = 20000
signal_size = 1100
output_dir = "/ramdisk/tmp_" + str(signal_size) + "/"
active_color = np.array([255, 0, 0]) / 255
inactive_color = np.array([0, 0, 0]) / 255
centroid_color = np.array([0, 255, 0]) / 255
old_signal0_plus = None
x_data = None
y_data = None
rams = []
for i in range(signal_size):  # range(len(y)):

    _save = True
    filename = output_dir + str('%06d' % i) + '.png'
    ax.axis([_min - margin, _max + margin,
             _min - margin, _max + margin])
    #ax.set_adjustable('box')
    #ax.legend((filename), 'upper right', shadow=True)

    rr_start = i
    rr_stop = get_max_index_for_cumulative_sum_greater_then_value(signal, size, i)
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

    s_plus = len(signal0_plus)
    if x_data == None:
        x_data = signal0_plus.copy()
        y_data = signal0_minus.copy()

        ax.scatter(x_data, y_data, c=active_color, s=20)
        ax.scatter([mean_plus], [mean_minus], s=80, c=centroid_color) # @IgnorePep8        

    else:
        old_s_plus = len(old_signal0_plus)
        ok = False

        if s_plus >= old_s_plus:
            for idx in xrange(1, old_s_plus):
                if np.all(old_signal0_plus[idx:] \
                            == signal0_plus[idx - 1: old_s_plus - idx]):
                    x_data = np.hstack((x_data, signal0_plus[old_s_plus - idx:])) # @IgnorePep8
                    y_data = np.hstack((y_data, signal0_minus[old_s_plus - idx:])) # @IgnorePep8
                    inactive_size = len(x_data) - s_plus
                    ax.scatter(x_data[:inactive_size], y_data[:inactive_size],
                               s=20, c=inactive_color)
                    ax.scatter(x_data[inactive_size:], y_data[inactive_size:],
                               s=20, c=active_color)
                    ax.scatter([mean_plus], [mean_minus], s=80,
                               c=centroid_color, label='filename')
                    #ax.legend((filename), 'upper right', shadow=True)
                    ok = True
                    break
        else:
            for idx in xrange(1, old_s_plus):
                if idx + s_plus <= old_s_plus \
                    and np.all(old_signal0_plus[idx:idx + s_plus] \
                                == signal0_plus):
                    inactive_size = len(x_data) - old_s_plus + idx
                    ax.scatter(x_data[:inactive_size], y_data[:inactive_size],
                               s=20, c=inactive_color)
                    ax.scatter(x_data[inactive_size + s_plus:],
                               y_data[inactive_size + s_plus:],
                               s=20, c=inactive_color)
                    ax.scatter(x_data[inactive_size:inactive_size + s_plus],
                               y_data[inactive_size:inactive_size + s_plus],
                               s=20, c=active_color)
                    ax.scatter([mean_plus], [mean_minus], s=80,
                               c=centroid_color)
                    ok = True
                    #_save = False
                    break
        if ok == False:
            print('s_plus: ' + str(s_plus) + ' old_s_plus: ' + str(old_s_plus)) # @IgnorePep8
            print('old_signal0_plus: ' + str(old_signal0_plus))
            print('signal0_plus:     ' + str(signal0_plus))
            raise Exception('Error for ' + str(i))

    old_signal0_plus = signal0_plus
    #
    # Notice the use of LaTeX-like markup.
    #
    #title(r'$\cal{N}(\mu, \sigma^2)$', fontsize=20)

    #ram = cStringIO.StringIO()
    #fig.savefig(ram, format='raw', dpi=100)
    #ram.close()
    #rams.append(ram)

    #_save = False
    #filename = str('%06d' % i) + '.png'
    if _save:
        savefig(filename, dpi=100)
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
           'type=png:w=1024:h=1024:fps=120',
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
#mencoder mf:///ramdisk/tmp/*.png -mf type=png:w=1024:h=800:fps=30 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output.avi


#bin=StringIO()
#bin.write("/x5F/x5F%c" % 0xFF)

#file = open ("my.bin","wb")
#file.write(bin.getvalue())
#file.close()
