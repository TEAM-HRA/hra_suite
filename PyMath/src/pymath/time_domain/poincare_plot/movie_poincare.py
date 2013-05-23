# This example uses a MovieWriter directly to grab individual frames and
# write them to a file. This avoids any event loop integration, but has
# the advantage of working with even the Agg backend. This is not recommended
# for use in an interactive setting.
# -*- noplot -*-

import matplotlib
import argparse
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import pylab as pl
import sys
import glob


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

#FFMpegWriter = manimation.writers['ffmpeg']
#metadata = dict(title='Movie Test', artist='Matplotlib',
#        comment='Movie support!')
#writer = FFMpegWriter(fps=15, metadata=metadata)
#
#fig = plt.figure()
#l, = plt.plot([], [], 'k-o')
#
#plt.xlim(-5, 5)
#plt.ylim(-5, 5)
#
#x0,y0 = 0, 0
#
#with writer.saving(fig, "test_poincare.mp4", 100):
#    for i in range(100):
#        x0 += 0.1 * np.random.randn()
#        y0 += 0.1 * np.random.randn()
#        l.set_data(x0, y0)
#        writer.grab_frame()


A_HALF = pl.float64(0.5)


def get_range(sample, signal, count, mode=1):
    if mode == 1:
        return range(len(sample) - count)
    elif mode == 2:
        return range(len(signal))
    elif mode == 3:
        return range(len(signal) - count)


class DummyIterator(object):
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def get_iterator(writer, fig, movie_filename):
    if writer == None:
        return DummyIterator()
    else:
        return writer.saving(fig, movie_filename, 150)


def test_poincare_resampled(filename, s_index, step, count,
                            create_movie=False, mode=1, fps=95,
                            show_window_statistics=False):

    print(' ')
    print(50 * '*')
    shift = 1
    signal = pl.loadtxt(filename, skiprows=1, usecols=[s_index], unpack=True)
    #signal = pl.around(signal, 0)

    _sum = pl.sum(signal)
    _max = pl.amax(signal)
    _min = pl.amin(signal)
    _mean = pl.mean(signal)
    _median = pl.median(signal)
    print('FILE: ' + str(filename) + ' step: '
           + str(step) + ' count: ' + str(count))
    print('SIGNAL: count: {0}  {1}  '.format(len(signal), signal))
    print('sum: {0} median: {1} [min, mean, max] => [{2}, {3}, {4}] '.format( # @IgnorePep8
                                        _sum, _median, _min, _mean, _max))

    sample = pl.arange(0, sum(signal), step)
    cumsum = pl.cumsum(signal)
    size = step * count

    writer = None
    fig = None

    if create_movie:
        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                        comment='Movie support!')
        writer = FFMpegWriter(fps=fps, metadata=metadata)

        fig = plt.figure()
        #l, = plt.plot([], [], 'k-o')
        l, = plt.plot([], [], 'bo')

        margin = 50
        plt.xlim(_min - margin, _max + margin)
        plt.ylim(_min - margin, _max + margin)

        x0 = 0
        y0 = 0

    symmetry_d = []
    symmetry_a = []
    equals = 0

    sd1a_count = 0
    sd1d_count = 0
    sd1_equal_count = 0

    rr_start_old = -1
    rr_stop_old = -1
    movie_filename = filename + ".mp4"
    with get_iterator(writer, fig, movie_filename):

        for i in get_range(sample, signal, count, mode):

            if mode == 1:
                rr_start = pl.searchsorted(cumsum, sample[i])
                rr_stop = pl.searchsorted(cumsum, sample[i + count])
                indexes = pl.arange(rr_start, rr_stop)
            elif mode == 2:
                rr_start = i
                rr_stop = get_max_index_for_cumulative_sum_greater_then_value(
                                                            signal, size, i)
                if rr_stop == -1:
                    break
                indexes = pl.arange(rr_start, rr_stop)
            elif mode == 3:
                rr_start = i
                rr_stop = i + count
                indexes = pl.arange(rr_start, rr_stop + 1)

            signal0 = signal.take(indexes)
            if show_window_statistics:
                print('')
                print('-' * 50)
                print('index {0}'.format(i))
                print('rr_start: {0} rr_stop {1}'.format(rr_start, rr_stop))
                print('sum: {0}  median: {1}  [min, mean, max] => [{2}, {3}, {4}] '.format( # @IgnorePep8
                                                        pl.sum(signal0),
                                                        pl.median(signal0),
                                                        pl.amin(signal0),
                                                        pl.mean(signal0),
                                                        pl.amax(signal0),
                                                        ))
            #print(pl.sum(signal0))

            indexes_plus = pl.arange(0, len(signal0) - 1)
            signal0_plus = signal0.take(indexes_plus)

            indexes_minus = pl.arange(1, len(signal0))
            signal0_minus = signal0.take(indexes_minus)

            if rr_start_old == rr_start and rr_stop_old == rr_stop:
                pass
            else:
                if not writer == None:
                    l.set_data(signal0_plus, signal0_minus)
                    writer.grab_frame()

            rr_start_old = rr_start
            rr_stop_old = rr_stop

            __d1 = (signal0_plus - signal0_minus) / pl.sqrt(2)
            s = len(__d1)

            sd1 = pl.sum(__d1 ** 2) / s
            indexes_1d = pl.find(__d1 < 0)
            indexes_1a = pl.find(__d1 > 0)
            sd1d_2 = pl.sum((__d1[indexes_1d]) ** 2) / s
            sd1a_2 = pl.sum((__d1[indexes_1a]) ** 2) / s
            if show_window_statistics:
                print('counts: [sd1, sd1_s, sd1d] => [{0}, {1}, {2}]  sd: [sd1^2, sd1a^2, sd1d^2] => [{3}, {4}, {5}]'.format(  # @IgnorePep8
                        len(__d1), len(indexes_1a), len(indexes_1d),
                        sd1, sd1a_2, sd1d_2))
            if sd1a_2 > sd1d_2:
                sd1a_count += 1
            elif sd1a_2 < sd1d_2:
                sd1d_count += 1
            else:
                sd1_equal_count += 1

            c1d = sd1d_2 / sd1
            c1a = sd1a_2 / sd1

            nochange_indexes = pl.find(__d1 == 0)

            mean0_plus = pl.mean(signal0_plus)
            mean0_minus = pl.mean(signal0_minus)

            __d2 = (signal0_plus - mean0_plus + signal0_minus - mean0_minus) / pl.sqrt(2) # @IgnorePep8

            sd2 = pl.sum(__d2 ** 2) / s

            sd2d_2 = (pl.sum(__d2[pl.find(__d1 < 0)] ** 2)
                    + (pl.sum(__d2[nochange_indexes] ** 2) / 2)) / s

            sd2a_2 = (pl.sum(__d2[pl.find(__d1 > 0)] ** 2)
                    + (pl.sum(__d2[nochange_indexes] ** 2) / 2)) / s

            sdnna_2 = (sd1a_2 + sd2a_2) / 2
            sdnnd_2 = (sd1d_2 + sd2d_2) / 2
            sdnn_2 = sdnna_2 + sdnnd_2

            ca = sdnna_2 / sdnn_2
            cd = sdnnd_2 / sdnn_2
#            m = pl.mean([ca, cd])
#            m_ca = pl.absolute(0.5-ca)

            #print('ca + cd: {0:.30f} + {1:.30f} m_ca: {2:.30f}'.format(ca, cd, m_ca)) # @IgnorePep8
            #if abs(ca - cd) > sys.float_info.epsilon:
            #    print('NOT EQUAL !!!')
            #    break

            #rounded = pl.around([ca, cd], 3)
            #ca_r = rounded[0]
            #cd_r = rounded[1]

            #print(str(c1d))
            if c1d > 0.5:
                symmetry_d.append(1)
                symmetry_a.append(0)
            elif c1d < 0.5:
                symmetry_d.append(0)
                symmetry_a.append(1)
            else:
                symmetry_d.append(0.5)
                symmetry_a.append(0.5)
                equals = equals + 1

    print('')
    print('SUMMARY STATISTICS:')
    print('symmetry counts: [sd1a = sd1d, sd1a > sd1d , sd1a < sd1d] => [{0}, {1}, {2}] '.format( # @IgnorePep8
                    sd1_equal_count, sd1a_count, sd1d_count))
    print('symmetry_d: ' + str(pl.mean(pl.array(symmetry_d)))
        + '  symmetry_a: ' + str(pl.mean(pl.array(symmetry_a)))
        + ' equals count: ' + str(equals))
    if not writer == None:
        print('')
        print('Movie ' + movie_filename + ' created')

if __name__ == '__main__':

    to_bool = lambda p: True if p.title() == "True" else False

#    filename = sys.argv[1]
#    signal_index = int(sys.argv[2])
#    step = int(sys.argv[3])
#    count = int(sys.argv[4])

    parser = argparse.ArgumentParser('Program to generate Poincare Plot parameters:') # @IgnorePep8
    parser.add_argument("-f", "--filename",  help="filename", default=None)
    parser.add_argument("-index", "--signal_index", type=int,
                        help="signal index [default 1]", default=1)
    parser.add_argument("-step", "--step", type=int,
                    help="resampling step in ms [default 100]", default=100)
    parser.add_argument("-multi", "--multiplicity", type=int,
                        help="""multiplicity (step*multiplicity == window size)
                                [default 3000] (30000 ms = 5m window size)""",
                                default=3000)
    parser.add_argument("-d", "--directory",
                help="directory, this give ability to generate for many files",
                default=None)
    parser.add_argument("-ext", "--extension",
                help="extension of files [default: rea]", default="rea")
    parser.add_argument("-movie", "--create_movie",
                help="""during processing create poincare plot movie
                        Warning ! requires codecs: ffmpeg, ffplay, ffprobe
                        [default: False]""",
                type=to_bool, default=False)
    parser.add_argument("-mode", "--mode", type=int,
                        help="""mode: 1 - timed with resampling,
                        2 - timed without resampling, 3 - bited [default 1]""",
                        default=1)
    parser.add_argument("-fps", "--fps", type=int,
                        help="fps value for a movie [default 95]", default=95)
    parser.add_argument("-show_stat", "--show_window_statistics",
                    help="show some data window statistics [default False]",
                    type=to_bool, default=False)
    __args = parser.parse_args()

    if __args.directory == None and __args.filename == None:
        print('Filename or directory is required')
    else:
        if not __args.directory == None:
            print("DIR: " + str(__args.directory))
            filenames = glob.glob(__args.directory + '\\*.' + __args.extension)

            for _filename in filenames:
                test_poincare_resampled(_filename, __args.signal_index,
                        __args.step, __args.multiplicity, __args.create_movie,
                        __args.mode, __args.fps, __args.show_window_statistics)
        else:
            test_poincare_resampled(__args.filename, __args.signal_index,
                        __args.step, __args.multiplicity, __args.create_movie,
                        __args.mode, __args.fps, __args.show_window_statistics)
    print('************* THE END ******************')
