#!/usr/bin/python
#
# Josh Lifton 2004
#
# Permission is hereby granted to use and abuse this document
# so long as proper attribution is given.
#
# This Python script demonstrates how to use the numarray package
# to generate and handle large arrays of data and how to use the
# matplotlib package to generate plots from the data and then save
# those plots as images.  These images are then stitched together
# by Mencoder to create a movie of the plotted data.  This script
# is for demonstration purposes only and is not intended to be
# for general use.  In particular, you will likely need to modify
# the script to suit your own needs.
#
import os                         # For issuing commands to the OS.
import sys                        # For determining the Python version.
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig, plot, xlabel, ylabel, title, clf, axis
from numpy.numarray.numerictypes import Float64
from matplotlib.collections import PathCollection


def get_signal():
    return [
            725.000000,
            745.000000,
            750.000000,
            740.000000,
            720.000000,
            700.000000,
            690.000000,
            680.000000,
            670.000000,
            695.000000,
            690.000000,
            730.000000,
            750.000000,
            730.000000,
            745.000000,
            740.000000,
            750.000000,
            740.000000,
            725.000000,
            700.000000,
            705.000000,
            695.000000,
            675.000000,
            670.000000,
            670.000000,
            675.000000,
            685.000000,
            680.000000,
            685.000000,
            685.000000,
            700.000000,
            715.000000,
            710.000000,
            725.000000,
            730.000000,
            730.000000,
            720.000000,
            710.000000,
            715.000000,
            715.000000,
            705.000000,
            705.000000,
            695.000000,
            680.000000,
            685.000000,
            660.000000,
            670.000000,
            675.000000,
            655.000000,
            675.000000,
            670.000000,
            665.000000,
            620.000000,
            640.000000,
            645.000000,
            645.000000,
            660.000000,
            685.000000,
            695.000000,
            675.000000,
            635.000000,
            645.000000,
            660.000000,
            655.000000,
            680.000000,
            645.000000,
            665.000000,
            650.000000,
            690.000000,
            700.000000,
            715.000000,
            725.000000,
            715.000000,
            695.000000,
            680.000000,
            680.000000,
            665.000000,
            655.000000,
            650.000000,
            650.000000,
            635.000000,
            645.000000,
            645.000000,
            640.000000,
            635.000000,
            630.000000,
            635.000000,
            630.000000,
            645.000000,
            630.000000,
            640.000000,
            655.000000,
            680.000000,
            655.000000,
            670.000000,
            700.000000,
            685.000000,
            665.000000,
            665.000000,
            655.000000
            ]


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
# Print the version information for the machine, OS,
# Python interpreter, and matplotlib.  The version of
# Mencoder is printed when it is called.
#
# This script is known to have worked for:
#
# OS version: ('Linux', 'flux-capacitor', '2.4.26', '#1 SMP Sa Apr 17 19:33:42
#         CEST 2004', 'i686')
# Python version: 2.3.4 (#2, May 29 2004, 03:31:27) [GCC 3.3.3 (Debian 20040417)]
# matplotlib version: 0.61.0
# MEncoder version:
# MEncoder 1.0pre4-3.3.3 (C) 2000-2004 MPlayer Team
# CPU: Intel Celeron 2/Pentium III Coppermine,Geyserville 996.1 MHz (Family: 6,
#  Stepping: 10)
# Detected cache-line size is 32 bytes
# CPUflags: Type: 6 MMX: 1 MMX2: 1 3DNow: 0 3DNow2: 0 SSE: 1 SSE2: 0
# Compiled for x86 CPU with extensions: MMX MMX2 SSE
#
print 'Executing on', os.uname()
print 'Python version', sys.version
#print 'matplotlib version', matplotlib.__version__

#
# First, let's create some data to work with.  In this example
# we'll use a normalized Gaussian waveform whose mean and
# standard deviation both increase linearly with time.  Such a
# waveform can be thought of as a propagating system that loses
# coherence over time, as might happen to the probability
# distribution of a clock subjected to independent, identically
# distributed Gaussian noise at each time step.
#


print 'Initializing data set...'  # Let the user know what's happening.


# Initialize variables needed to create and store the example data set.
numberOfTimeSteps = 100   # Number of frames we want in the movie.
x = np.arange(-10, 10, 0.01)   # Values to be plotted on the x-axis.
mean = -6                 # Initial mean of the Gaussian.
stddev = 0.2              # Initial standard deviation.
meaninc = 0.1             # Mean increment.
stddevinc = 0.1           # Standard deviation increment.

# Create an array of zeros and fill it with the example data.
y = np.zeros((numberOfTimeSteps, len(x)), Float64)
for i in range(numberOfTimeSteps):
    y[i] = (1 / np.sqrt(2 * np.pi * stddev)) \
                * np.exp(-((x - mean) ** 2) / (2 * stddev))
    mean = mean + meaninc
    stddev = stddev + stddevinc

print 'Done.'                       # Let the user know what's happening.

#
# Now that we have an example data set (x,y) to work with, we can
# start graphing it and saving the images.
#
s_index = 1
#filename = "/home/jurek/volumes/doctoral/dane/24h/part1/ANDRZ29.rea"
filename = "/home/jurek/tmp/movie_poincare.rea"
signal = pl.loadtxt(filename, skiprows=1, usecols=[s_index], unpack=True)
signal = signal[signal < 5000]

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

fig = plt.figure()


l, = plt.plot([], [], 'bo')

margin = 50

plt.xlim(_min - margin, _max + margin)
plt.ylim(_min - margin, _max + margin)

signal_size = len(signal)
signal_size = 10000
active_color = np.array([255, 0, 0]) / 255
inactive_color = np.array([0, 0, 0]) / 255
centroid_color = np.array([0, 255, 0]) / 255
white_color = np.array([255, 255, 255]) / 255
old_indexes_plus = None
old_indexes_minus = None
old_signal0 = None
colors = None
old_indexes = None
old_signal0_plus = None
old_signal0_minus = None
_min = 500
_max = 800
old_mean_plus = None
old_mean_minus = None
list_plus = []
list_minus = []
rr_start_old = None
rr_stop_old = None


signal = np.array(get_signal())  # np.random.random(100) * 1000
print('S: ' + str(signal))
size = 10000
signal_size = 10
#plt.ion()
#plt.show()
for i in range(signal_size):  # range(len(y)):
    #
    # The next four lines are just like Matlab.
    #

    rr_start = i
    rr_stop = get_max_index_for_cumulative_sum_greater_then_value(signal, size, i)
    if rr_stop == -1:
        break
    indexes = pl.arange(rr_start, rr_stop)
    print('rr_start: ' + str(rr_start) + ' rr_stop: ' + str(rr_stop) +
          ' indexes: ' + str(indexes))

    signal0 = signal.take(indexes)

    indexes_plus = pl.arange(0, len(signal0) - 1)
    signal0_plus = signal0.take(indexes_plus)

    indexes_minus = pl.arange(1, len(signal0))
    signal0_minus = signal0.take(indexes_minus)

    mean_plus = pl.mean(signal0_plus)
    mean_minus = pl.mean(signal0_minus)

    #l, = plt.plot([], [])  # , 'bo')
    #l.sc, = plt.scatter([], [])
    #plot(x, y[i], 'b.')
    #axis((x[0], x[-1], -0.25, 1))
    #xlabel('time (ms)')
    #l.ylabel('probability density function')

    #list_plus[len(list_plus):] = signal0_plus.tolist()
    #list_minus[len(list_minus):] = signal0_minus.tolist()

    #l.set_data(list_plus, list_minus)

#    if i == 1:
#        plt.plot(signal0_plus, signal0_minus, c=active_color)
#    else:
#        plt.plot(signal0_plus, signal0_minus, c=inactive_color)

    #l.set_data(signal0_plus * 3, signal0_minus * 3)

    #colors = (len(signal0_plus) / 2) * [inactive_rgb / 255] + \
    #        (len(signal0_plus) / 2) * [active_rgb / 255]
    #colors = 10 * [inactive_rgb / 255] + \
    #        2 * [active_rgb / 255]
    #if not old_mean_plus == None:
    #    plt.scatter([old_mean_plus],
    #                [old_mean_minus],
    #                color=white_color, s=2)

    #plt.scatter([mean_plus],
    #            [mean_minus],
    #            color=centroid_color, s=2)

    #l.set_data()
    #plt.plot(signal_plus, signal_minus, c=active_color)
    #plt.draw()
    if old_indexes == None:
        x_data = signal0_plus
        y_data = signal0_minus
        print('x_data: ' + str(x_data))
        print('y_data: ' + str(y_data))
        #_scatter = plt.scatter(signal0_plus, signal0_minus,
        #                     color=active_color,  s=2)
        _scatter = plt.scatter(x_data, y_data,
                               color=active_color,
                               s=2)
    else:
        if rr_start_old == rr_start and rr_stop_old == rr_stop:
            continue

        inactive_value_plus = signal0_plus[0]
        inactive_value_minus = signal0_minus[0]
        idx_inactive = 0
        while True:
            if old_signal0_plus[idx_inactive] == inactive_value_plus \
                and old_signal0_minus[idx_inactive] == inactive_value_minus:
                    break
            idx_inactive = idx_inactive + 1

        active_value_plus = old_signal0_plus[-1]
        active_value_minus = old_signal0_minus[-1]
        idx_active = -1
        while True:
            if signal0_plus[idx_active] == active_value_plus \
                and signal0_minus[idx_active] == active_value_minus:
                    break
            idx_active = idx_active - 1

        # idx_active is a negative value
        _s = len(signal0_plus)
        # idx_active is a negative value
        active_indexes = pl.arange(_s + idx_active + 1, _s)
        #print('active_indexes: ' + str(len(active_indexes)))
        if not len(active_indexes) > 0:
            continue

        x_data = np.hstack((x_data, signal0_plus.take(active_indexes)))
        y_data = np.hstack((y_data, signal0_minus.take(active_indexes)))

        _scatter.set_offsets([x_data, y_data])

        print('active_indexes: ' + str(active_indexes))
        print('x_data: ' + str(x_data))
        print('y_data: ' + str(y_data))

#        inactive_size = len(np.setdiff1d(old_indexes, indexes))
#        if inactive_size > 0:
#            inactive_signal0_plus = old_signal0_plus.take(pl.arange(inactive_size))  # @IgnorePep8
#            x_data = np.hstack((inactive_signal0_plus, x_data))
#
#            inactive_signal0_minus = old_signal0_minus.take(pl.arange(inactive_size))  # @IgnorePep8
#            y_data = np.hstack((inactive_signal0_minus, y_data))
#
#        active_size = len(np.setdiff1d(indexes, old_indexes))

        #plt.draw()

    #        list_plus[len(list_plus):] = signal0_plus.tolist()
    #        list_minus[len(list_minus):] = signal0_minus.tolist()
    #
#        inactive_indexes_plus = np.setdiff1d(old_indexes_plus, indexes_plus)
#        if len(inactive_indexes_plus):
#            pass
#        inactive_indexes_minus = np.setdiff1d(old_indexes_minus,indexes_minus)
        #_scatter(signal.take(inactive_indexes_plus),
        #            signal.take(inactive_indexes_minus),
        #            color=inactive_color, s=2)

        #active_indexes_plus = np.setdiff1d(indexes_plus, old_indexes_plus)
        #active_indexes_minus = np.setdiff1d(indexes_minus, old_indexes_minus)

        #_scatter.set_offsets([signal0_plus, signal0_minus])

        #plt.scatter(signal.take(active_indexes_plus),
        #            signal.take(active_indexes_minus),
        #            color=active_color, s=2)
    #
    #        #plt.scatter(signal.take(inactive_plus),
    #        #            signal.take(inactive_minus),
    #        #            color=inactive_color, s=2)
    #        #print('inactive_plus_values: '
    #        #      + str(old_signal0.take(diff_inactive_indexes_plus)))
    #        #print('diff_inactive_indexes_minus: ' + str(diff_inactive_indexes_minus)) # @IgnorePep8
    #        #print('inactive_minus_values: '
    #        #      + str(old_signal0.take(diff_inactive_indexes_minus)))
    #        #plt.scatter(old_signal0.take(diff_inactive_indexes_plus),
    #        #             old_signal0.take(diff_inactive_indexes_minus),
    #        #             color=inactive_color, s=2)
    #
    #        #active_plus = np.setdiff1d(indexes[:-1], old_indexes[:-1])
    #        #active_minus = np.setdiff1d(indexes[1:], old_indexes[1:])
    #
    #        #plt.scatter(signal.take(active_plus),
    #        #            signal.take(active_minus),
    #        #            color=active_color, s=2)

    #plt.scatter([mean_plus],
    #            [mean_minus],
    #            color=centroid_color, s=2)

    #_scatter.set_offsets([list_plus, list_minus])

    #plt.scatter(list_plus, list_minus,
    #            #signal0_plus, signal0_minus,
    #                color=active_color,
    #                s=2)
#    _scatter.set_offsets(np.array([
#                                [signal.take(inactive_plus).tolist(),
#                                   signal.take(inactive_minus).tolist()]
#    ]))

    old_mean_plus = mean_plus
    old_mean_minus = mean_minus
        #print('inactive plus: ' + str(diff_inactive_indexes_plus) +
        #      'inactive minus: ' + str(diff_inactive_indexes_minus) +
        #      'active plus: ' + str(diff_active_indexes_plus) +
        #      'active minus: ' + str(diff_active_indexes_minus))

        #plt.scatter(signal.take(diff_active_indexes_plus),
        #            signal.take(diff_active_indexes_minus),
        #            color=active_color, s=2)

    old_indexes_plus = indexes_plus
    old_indexes_minus = indexes_minus
    old_signal0 = signal0
    old_indexes = indexes
    old_signal0_plus = signal0_plus
    old_signal0_minus = signal0_minus

    rr_start_old = rr_start
    rr_stop_old = rr_stop
    #print('type: ' + str(l))

    #
    # Notice the use of LaTeX-like markup.
    #
    #title(r'$\cal{N}(\mu, \sigma^2)$', fontsize=20)

    #
    # The file name indicates how the image will be saved and the
    # order it will appear in the movie.  If you actually wanted each
    # graph to be displayed on the screen, you would include commands
    # such as show() and draw() here.  See the matplotlib
    # documentation for details.  In this case, we are saving the
    # images directly to a file without displaying them.
    #
    filename = str('%03d' % i) + '.png'
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
    #plt.cla()

#
# Now that we have graphed images of the dataset, we will stitch them
# together using Mencoder to create a movie.  Each image will become
# a single frame in the movie.
#
# We want to use Python to make what would normally be a command line
# call to Mencoder.  Specifically, the command line call we want to
# emulate is (without the initial '#'):
# mencoder mf://*.png -mf type=png:w=800:h=600:fps=25 -ovc lavc -lavcopts
# vcodec=mpeg4 -oac copy -o output.avi
# See the MPlayer and Mencoder documentation for details.
#

command = ('mencoder',
           'mf://*.png',
           '-mf',
           'type=png:w=800:h=600:fps=25',
           '-ovc',
           'lavc',
           '-lavcopts',
           'vcodec=mpeg4',
           '-oac',
           'copy',
           '-o',
           'output.avi')

os.spawnvp(os.P_WAIT, 'mencoder', command)

#command = ('rm ', '*.png')
#os.spawnvp(os.P_WAIT, 'mencoder', command)


