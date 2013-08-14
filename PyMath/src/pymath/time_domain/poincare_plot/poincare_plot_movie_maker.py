from pymath.utils.utils import print_import_error
from pycore.collections_utils import get_chunks
try:
    import os
    import gc
    import multiprocessing
    import pylab as pl
    #from matplotlib.pyplot import savefig
    #matplotlib.use("Agg")
    #import matplotlib.pyplot as plt
    #from matplotlib.patches import Rectangle
    from pycore.datetime_utils import get_time_label_for_miliseconds
    from pycore.misc import Params
    from pycore.misc import ColorRGB
    from pycore.io_utils import as_path
except ImportError as error:
    print_import_error(__name__, error)


def get_color_array(_color):
    """
    method converts _color parameter into numpy array
    """
    if isinstance(_color, ColorRGB):
        return pl.array([_color.red, _color.green, _color.blue]) / 255.0


class PoincarePlotMovieMaker(object):
    """
    class used to generate poincare plot movie
    """
    def __init__(self, data_vector, movie_parameters, **params):
        self.p = movie_parameters
        if not self.p.movie_name == None:
            self.params = Params(**params)

            if not self.params.filter_manager == None:
                data_vector = self.params.filter_manager.run_filters(
                                                                data_vector)
            _max = pl.amax(data_vector.signal)
            _min = pl.amin(data_vector.signal)

            margin = 50
            self.range = [_min - margin, _max + margin,
                          _min - margin, _max + margin]
            self.x_data = None
            self.y_data = None
            self.old_signal_plus = None
            #self.empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
            #                                 edgecolor='none', linewidth=0)
            self.idx = 0
            self.active_color = get_color_array(
                                        movie_parameters.movie_active_color)
            self.inactive_color = get_color_array(
                                        movie_parameters.movie_inactive_color)
            self.centroid_color = get_color_array(
                                        movie_parameters.movie_centroid_color)
            self.message = None
            self.pp_specs = []
            self.core_nums = multiprocessing.cpu_count() * self.p.movie_multiprocessing_factor # @IgnorePep8
            #self.start_idx = 0
            self.pp_spec_manager = MiniPoincarePlotSpecManager()

    def add_data_vector_segment(self, data_vector_segment, last_segment=False):
        self.message = None
        if self.p.movie_name == None:
            return

        if last_segment:
            self.__save_frames__()
            return
        #print('\nSTART data_vector_segment.signal_plus: ' + str(data_vector_segment.signal_plus))
        #return

        frame_file = as_path(self.p.movie_dir, '%06d.png' % self.idx)
        skip_frame = True if self.idx < self.p.movie_start_frame or \
            (self.p.movie_skip_frames and os.path.exists(frame_file)) \
            else False

        mean_plus = pl.mean(data_vector_segment.signal_plus)
        mean_minus = pl.mean(data_vector_segment.signal_minus)

        s_plus = len(data_vector_segment.signal_plus)

        pp_spec = MiniPoincarePlotSpec()
        pp_spec.s_plus = s_plus
        pp_spec.mean_plus = mean_plus
        pp_spec.mean_minus = mean_minus
        pp_spec.range = self.range
        pp_spec.active_color = self.active_color
        pp_spec.inactive_color = self.inactive_color
        pp_spec.centroid_color = self.centroid_color
        pp_spec.active_point_size = self.p.movie_active_size
        pp_spec.inactive_point_size = self.p.movie_inactive_size
        pp_spec.centroid_point_size = self.p.movie_centroid_size
        pp_spec.frame_file = frame_file
        pp_spec.show_plot_legends = self.p.movie_show_plot_legends

        self.pp_spec_manager.addMiniPoincarePlotSpec(pp_spec)

        #print('skip_frame: ' + str(skip_frame))
        if self.x_data == None:
            self.x_data = pl.copy(data_vector_segment.signal_plus)
            self.y_data = pl.copy(data_vector_segment.signal_minus)
            ok = True
            old_s_plus = 0
            if skip_frame == False:
                #pp_spec.x_data = self.x_data[:]
                #pp_spec.y_data = self.y_data[:]
                pp_spec.level = 0
        else:

            old_s_plus = len(self.old_signal_plus)
            ok = False
            #idx = 0
            #kk = (self.old_signal_plus[idx:]
            # == data_vector_segment.signal_plus[idx - 1: old_s_plus - idx])
            #print('type self.old_signal_plus[idx:] ' + str(type(self.old_signal_plus[idx:])))
            #print('type data_vector_segment.signal_plus[idx - 1: old_s_plus - idx]: '
            #      + str(type(data_vector_segment.signal_plus[idx - 1: old_s_plus - idx])))
            #print('kk: ' + str(kk))
            if s_plus >= old_s_plus:
                #print('self.old_signal_plus: ' + str(self.old_signal_plus))
                #print('data_vector_segment.signal_plus: ' + str(data_vector_segment.signal_plus))
                if pl.all(self.old_signal_plus \
                            == data_vector_segment.signal_plus[:old_s_plus]):
                    old_size = len(self.x_data)
                    new_size = old_size + s_plus - old_s_plus
                    #print('(3) old_size: ' + str(old_size) + ' new_size: ' + str(new_size))

                    #pl.require(self.x_data, requirements=['OWNDATA'])
                    #print('(3) before resize: ' + str(len(self.x_data)))
                    self.x_data.resize((new_size), refcheck=False)
                    #print('(3) after resize: ' + str(len(self.x_data))
                    #              + ' self.x_data: ' + str(self.x_data))
                    #print('(3) old_s_plus: ' + str(old_s_plus) +
                    #      ' s_plus - old_s_plus = ' + str(s_plus - old_s_plus))
                    self.x_data.put(pl.arange(old_size, new_size),
                        data_vector_segment.signal_plus[old_s_plus - s_plus:])
                    #print('(3) after put x_data: ' + str(self.x_data))

                    self.y_data.resize((new_size), refcheck=False)
                    self.y_data.put(pl.arange(old_size, new_size),
                        data_vector_segment.signal_minus[old_s_plus - s_plus:])

                    if skip_frame == False:
                        inactive_idx = len(self.x_data) - s_plus

                        #pp_spec.x_data = self.x_data[:]
                        #pp_spec.y_data = self.y_data[:]
                        #print('inactive_idx: ' + str(inactive_idx))
                        pp_spec.inactive_idx = inactive_idx
                        pp_spec.level = 1
                    ok = True
                    #print('\nidx = 0 level 1')
                else:
                    for idx in xrange(1, old_s_plus):
                        #print('idx: ' + str(idx))
                        #print('\n type: self.old_signal_plus[idx:] - '
                        #      + str(type(self.old_signal_plus[idx:])))
                        #print('\n self.old_signal_plus[idx:] - '
                        #      + str(self.old_signal_plus[idx:]))
                        #print('\n type(data_vector_segment.signal_plus[idx - 1: old_s_plus - idx]) - ' + 
                        #      str(type(data_vector_segment.signal_plus[idx - 1: old_s_plus - idx])))                    
                        #print('\n data_vector_segment.signal_plus[idx - 1: old_s_plus - idx] - ' + 
                        #      str(data_vector_segment.signal_plus[idx - 1: old_s_plus - idx]))
                        #kk = (self.old_signal_plus[idx:]
                        #     == data_vector_segment.signal_plus[idx - 1: old_s_plus - idx])
                        #print('kk: ' + str(kk) + ' type(kk) ' + str(type(kk)))
                        #if   not False in (
                        #if (
                        #        not False in kk
                        #    ): # @IgnorePep8
                        if pl.all(self.old_signal_plus[idx:] \
                                    == data_vector_segment.signal_plus[idx - 1:
                                                            old_s_plus - idx]):
                            #print('\nidx = ' + str(idx) + ' level 1')
                            #self.x_data = pl.hstack((self.x_data,
                            #    data_vector_segment.signal_plus[old_s_plus -
                            #                                     idx:]))
                            #self.y_data = pl.hstack((self.y_data,
                            #    data_vector_segment.signal_minus[old_s_plus -
                            #                                      idx:]))

                            old_size = len(self.x_data)
                            new_size = old_size + s_plus - (old_s_plus - idx)

                            self.x_data.resize((new_size), refcheck=False)
                            self.x_data.put(pl.arange(old_size, new_size),
                                data_vector_segment.signal_plus[
                                                           old_s_plus - idx:])

                            self.y_data.resize((new_size), refcheck=False)
                            self.y_data.put(pl.arange(old_size, new_size),
                                data_vector_segment.signal_minus[
                                                           old_s_plus - idx:])

                            if skip_frame == False:
                                inactive_idx = len(self.x_data) - s_plus

                                #pp_spec.x_data = self.x_data[:]
                                #pp_spec.y_data = self.y_data[:]
                                pp_spec.inactive_idx = inactive_idx
                                pp_spec.level = 1

                            ok = True
                            break
            else:
                for idx in xrange(1, old_s_plus):
                    if idx + s_plus <= old_s_plus \
                        and pl.all(
                            self.old_signal_plus[idx:idx + s_plus] \
                                    == data_vector_segment.signal_plus):
                        if skip_frame == False:
                            inactive_idx = len(self.x_data) - old_s_plus + idx

                            #pp_spec.x_data = self.x_data[:]
                            #pp_spec.y_data = self.y_data[:]
                            #pp_spec.x_size = len(self.x_data)
                            #pp_spec.y_size = len(self.y_data)
                            pp_spec.inactive_idx = inactive_idx
                            pp_spec.level = 2
                            #print('\nidx = ' + str(idx) + ' level 2')

                        ok = True
                        break
        if ok == True and skip_frame == False:
            pp_spec.x_data = self.x_data
            pp_spec.y_data = self.y_data
            pp_spec.d_size = len(self.x_data)
            #pp_spec.y_size = len(self.y_data)
            #print('x_size: ' + str(pp_spec.x_size))
            #print('y_size: ' + str(pp_spec.y_size))
            #if self.idx == 0:
            #    create_mini_poincare_plot(pp_spec)

            if self.p.movie_multiprocessing_factor > 0:
                if self.idx > 0 and self.idx % 500 == 0:
                    self.pp_specs.append(self.pp_spec_manager)
                    self.pp_spec_manager = MiniPoincarePlotSpecManager()
                #print('FRAME FILE ADDED:' + str(pp_spec.frame_file))
                #self.pp_specs.append(pp_spec)
                if len(self.pp_specs) > self.core_nums:  # self.core_nums:
                    #create_mini_poincare_plot_v2(self.pp_specs,
                    #                             self.p.movie_dir,
                    #                             self.start_idx)
                    #self.start_idx = self.start_idx + len(self.pp_specs)
                    #self.__save_frames__()
                    #self.pp_specs = []
                    self.__save_frames__()
            else:
                create_mini_poincare_plot(pp_spec)
            self.message = 'Wrote file: %s' % (frame_file)
        elif ok == True and skip_frame == True:
            self.message = 'File %s skipped' % (frame_file)
        elif ok == False:
            print('s_plus: ' + str(s_plus) + ' old_s_plus: ' + str(old_s_plus))
            print('old_signal_plus: ' + str(self.old_signal_plus))
            print('signal_plus:     ' + str(data_vector_segment.signal_plus))
            raise Exception('Error for idx ' + str(self.idx))

        self.old_signal_plus = data_vector_segment.signal_plus
        self.idx = self.idx + 1
        #if self.idx > 3:
        #    create_mini_poincare_plot(pp_spec)
        #    raise Exception('END')
        gc.collect()  # 'to force' garbage collection

    def save_movie(self):
        if not self.p.movie_name == None and self.p.movie_not_save == False:

            output_movie_file = as_path(self.p.movie_dir,
                                        '%s.avi' % (self.p.movie_name))
            command = ('mencoder',
                       'mf://' + self.p.movie_dir + '/*.png',
                       '-mf',
                       #'type=png:w=1024:h=800:fps=30',
                       'type=png:w=' + str(self.p.movie_width) + \
                            ':h=' + str(self.p.movie_height) + \
                            ':fps=' + str(self.p.movie_fps),
                       '-ovc',
                       'lavc',
                       '-lavcopts',
                       'vcodec=mpeg4',
                       '-oac',
                       'copy',
                       '-o',
                       '%s' % (output_movie_file))
            os.spawnvp(os.P_WAIT, 'mencoder', command)
            self.message = \
                "Poincare plot movie %s is created !" % (output_movie_file)

    @property
    def info_message(self):
        return self.message

#    def __save_frames_old__(self):
#        if not hasattr(self, 'pool'):
#            self.pool = multiprocessing.Pool(processes=self.core_nums,
#                            maxtasksperchild=self.core_nums)
#        #self.pool.map(create_mini_poincare_plot, self.pp_specs[:],
#        #         chunksize=self.p.movie_multiprocessing_factor)
#        self.pool.imap_unordered(create_mini_poincare_plot, self.pp_specs[:],
#                 chunksize=400)
#        self.pp_specs = []
#        gc.collect()  # 'to force' garbage collection

    def __save_frames__(self):
        import matplotlib.pyplot as plt
        #return
        # 1
        #print(' Saving')
        pool = multiprocessing.Pool(
                                    processes=self.core_nums,
                                    #processes=self.core_nums,
                    maxtasksperchild=self.p.movie_multiprocessing_factor)
        pool.map(create_mini_poincare_plot,
                            self.pp_specs,
                            #chunksize=multiprocessing.cpu_count())
                            #chunksize=self.p.movie_multiprocessing_factor
                            )
        #self.p.movie_multiprocessing_factor)
        # 2
        #pool = multiprocessing.Pool(processes=self.core_nums,
        #                maxtasksperchild=self.p.movie_multiprocessing_factor)
        #pool.imap_unordered(create_mini_poincare_plot, self.pp_specs,
        #         chunksize=multiprocessing.cpu_count() * 8)

        #pool.map(create_mini_poincare_plot, self.pp_specs[:],
        #         chunksize=self.p.movie_multiprocessing_factor)
        #oo = pool.imap_unordered(create_mini_poincare_plot, self.pp_specs,
        #         chunksize=100)
        #async = pool.map_async(create_mini_poincare_plot, self.pp_specs,
        #         chunksize=30)
        #async.wait()
        #print('TYPE: ' + str(type(oo)))
        pool.close()
        plt.close('all')
        self.pp_specs = []
        gc.collect()  # 'to force' garbage collection
        #print(' End saving')


class MiniPoincarePlotSpecManager(object):
    """
    class used to collect MiniPoincarePlotSpec objects,
    the class is introduced because of multiprocesing pool functionality,
    the method Pool.map doesn't work if an iterable parameter contains
    subarrays it have to be usual not iterable objects
    """
    def __init__(self):
        self.__pp_specs__ = []

    def addMiniPoincarePlotSpec(self, pp_spec):
        self.__pp_specs__.append(pp_spec)

    def getMiniPoincarePlotSpecs(self):
        return self.__pp_specs__


class MiniPoincarePlotSpec(object):
    """
    class used to store some important properties of mini-poincare plot
    """

    def __init__(self):
        self.__x_data__ = None
        self.__y_data__ = None
        self.__idx__ = None
        self.__level__ = None
        self.__inactive_idx__ = None
        self.__s_plus__ = None
        self.__mean_plus__ = None
        self.__mean_minus__ = None
        self.__range__ = None
        self.__active_color__ = None
        self.__inactive_color__ = None
        self.__centroid_color__ = None
        self.__active_point_size__ = None
        self.__inactive_point_size__ = None
        self.__centroid_point_size__ = None
        self.__frame_file__ = None
        self.__dpi__ = None
        self.__show_plot_legends__ = False
        self.__x_size__ = 0
        self.__y_size__ = 0

    @property
    def x_data(self):
        return self.__x_data__

    @x_data.setter
    def x_data(self, _x_data):
        self.__x_data__ = _x_data

    @property
    def y_data(self):
        return self.__y_data__

    @y_data.setter
    def y_data(self, _y_data):
        self.__y_data__ = _y_data

    @property
    def level(self):
        return self.__level__

    @level.setter
    def level(self, _level):
        self.__level__ = _level

    @property
    def inactive_idx(self):
        return self.__inactive_idx__

    @inactive_idx.setter
    def inactive_idx(self, _inactive_idx):
        self.__inactive_idx__ = _inactive_idx

    @property
    def s_plus(self):
        return self.__s_plus__

    @s_plus.setter
    def s_plus(self, _s_plus):
        self.__s_plus__ = _s_plus

    @property
    def mean_plus(self):
        return self.__mean_plus__

    @mean_plus.setter
    def mean_plus(self, _mean_plus):
        self.__mean_plus__ = _mean_plus

    @property
    def mean_minus(self):
        return self.__mean_minus__

    @mean_minus.setter
    def mean_minus(self, _mean_minus):
        self.__mean_minus__ = _mean_minus

    @property
    def range(self):
        return self.__range__

    @range.setter
    def range(self, _range):
        self.__range__ = _range

    @property
    def active_color(self):
        return self.__active_color__

    @active_color.setter
    def active_color(self, _active_color):
        self.__active_color__ = _active_color

    @property
    def inactive_color(self):
        return self.__inactive_color__

    @inactive_color.setter
    def inactive_color(self, _inactive_color):
        self.__inactive_color__ = _inactive_color

    @property
    def centroid_color(self):
        return self.__centroid_color__

    @centroid_color.setter
    def centroid_color(self, _centroid_color):
        self.__centroid_color__ = _centroid_color

    @property
    def active_point_size(self):
        return self.__active_point_size__

    @active_point_size.setter
    def active_point_size(self, _active_point_size):
        self.__active_point_size__ = _active_point_size

    @property
    def inactive_point_size(self):
        return self.__inactive_point_size__

    @inactive_point_size.setter
    def inactive_point_size(self, _inactive_point_size):
        self.__inactive_point_size__ = _inactive_point_size

    @property
    def centroid_point_size(self):
        return self.__centroid_point_size__

    @centroid_point_size.setter
    def centroid_point_size(self, _centroid_point_size):
        self.__centroid_point_size__ = _centroid_point_size

    @property
    def frame_file(self):
        return self.__frame_file__

    @frame_file.setter
    def frame_file(self, _frame_file):
        self.__frame_file__ = _frame_file

    @property
    def dpi(self):
        return self.__dpi__

    @dpi.setter
    def dpi(self, _dpi):
        self.__dpi__ = _dpi

    @property
    def show_plot_legends(self):
        return self.__show_plot_legends__

    @show_plot_legends.setter
    def show_plot_legends(self, _show_plot_legends):
        self.__show_plot_legends__ = _show_plot_legends

    @property
    def d_size(self):
        return self.__d_size__

    @d_size.setter
    def d_size(self, _d_size):
        self.__d_size__ = _d_size


def create_mini_poincare_plot(pp_spec_or_pp_specs_manager):
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import savefig
    print('create_mini_poincare_plot')
    #matplotlib.use("Agg")
    #import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    #print('IN create_mini_poincare_plot')
    #plt.ioff()
    if isinstance(pp_spec_or_pp_specs_manager, MiniPoincarePlotSpecManager):
        pp_specs = pp_spec_or_pp_specs_manager.getMiniPoincarePlotSpecs()
    else:
        pp_specs = [pp_spec_or_pp_specs_manager]
    p = pp_specs[0]  # alias
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
    ax.axis(p.range)
    ax.set_xlabel('$RR_{n}$ [ms]')
    ax.set_ylabel('$RR_{n+1}$ [ms]')
    empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                                edgecolor='none', linewidth=0)
    idx = 0
    for p in pp_specs:
        idx += 1
        if idx % 100:
            gc.collect()  # 'to force' garbage collection

        if p.level == 0:
            time_label = get_time_label_for_miliseconds(0)
        else:
            time_label = get_time_label_for_miliseconds(
                                    pl.sum(p.x_data[:p.inactive_idx]))
        leg_time = ax.legend([empty_rectangle], [time_label],
                              'upper left')
        leg_time.get_frame().set_alpha(0.5)
        ltext = leg_time.get_texts()
        plt.setp(ltext, fontsize=8)
        ax.add_artist(leg_time)

        a_plot = None
        c_plot = None
        i_plot_0 = None
        i_plot = None
        if p.level == 0:
            a_plot = ax.scatter(p.x_data, p.y_data,
                                c=p.active_color,
                                s=p.active_point_size)
            c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                                c=p.centroid_color,
                                s=p.centroid_point_size)
        elif p.level == 1:
            i_plot = ax.scatter(p.x_data[:p.inactive_idx],
                                p.y_data[:p.inactive_idx],
                                c=p.inactive_color,
                                s=p.inactive_point_size)
            a_plot = ax.scatter(p.x_data[p.inactive_idx:p.d_size],
                                p.y_data[p.inactive_idx:p.d_size],
                                c=p.active_color,
                                s=p.active_point_size)
            c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                                c=p.centroid_color,
                                s=p.centroid_point_size)
        elif p.level == 2:
            i_plot_0 = ax.scatter(p.x_data[:p.inactive_idx],
                                  p.y_data[:p.inactive_idx],
                                  c=p.inactive_color,
                                  s=p.inactive_point_size)
            i_plot = ax.scatter(p.x_data[p.inactive_idx + p.s_plus:p.d_size],
                                p.y_data[p.inactive_idx + p.s_plus:p.d_size],
                                c=p.inactive_color,
                                s=p.inactive_point_size)
            a_plot = ax.scatter(p.x_data[p.inactive_idx:p.inactive_idx + p.s_plus], # @IgnorePep8
                                p.y_data[p.inactive_idx:p.inactive_idx + p.s_plus], # @IgnorePep8
                                c=p.active_color,
                                s=p.active_point_size)
            c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                                c=p.centroid_color,
                                s=p.centroid_point_size)

        if p.show_plot_legends == True:

            if p.level == 0:
                leg_plots = ax.legend((a_plot, c_plot),
                                       ('biezacy PP', "controid"),
                                       'upper right', scatterpoints=1)
            else:
                leg_plots = ax.legend((a_plot, i_plot, c_plot),
                            ('biezacy PP', "poprzednie PP", "controid"),
                            'upper right', scatterpoints=1)  # , shadow=True)
            leg_plots.get_frame().set_alpha(0.5)
            ltext = leg_plots.get_texts()
            plt.setp(ltext, fontsize=8)

        #frame_file = as_path(p.frame_file_dir, '%06d.png' % idx)
        savefig(p.frame_file, dpi=p.dpi)
        #print('saving: ' + p.frame_file)

        if not a_plot == None:
            a_plot.remove()
        if not c_plot == None:
            c_plot.remove()
        if not i_plot == None:
            i_plot.remove()
        if not i_plot_0 == None:
            i_plot_0.remove()

        #remove legends
        leg_time.remove()
        if p.show_plot_legends == True:
            leg_plots.remove()
        ax.legend_ = None

    #savefig(p.frame_file, dpi=p.dpi)
    #print('saving frame: ' + p.frame_file)

    #print('FUNC saving frame: ' + p.frame_file)
    ax.cla()
    fig.clf()
    #plt.close()  # very important line, protects memory leaks
    fig = None
    #plt.close('all')
    #plt = None
    gc.collect()  # 'to force' garbage collection
    #print('SAVE PNG')


def create_mini_poincare_plot_v0(pp_spec):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.pyplot import savefig
    #print('IN create_mini_poincare_plot')
    #plt.ioff()
    p = pp_spec  # alias
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
    ax.axis(p.range)
    ax.set_xlabel('$RR_{n}$ [ms]')
    ax.set_ylabel('$RR_{n+1}$ [ms]')
    empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                                edgecolor='none', linewidth=0)
    if p.level == 0:
        time_label = get_time_label_for_miliseconds(0)
    else:
        time_label = get_time_label_for_miliseconds(
                                pl.sum(p.x_data[:p.inactive_idx]))
    leg_time = ax.legend([empty_rectangle], [time_label],
                          'upper left')
    leg_time.get_frame().set_alpha(0.5)
    ltext = leg_time.get_texts()
    plt.setp(ltext, fontsize=8)
    ax.add_artist(leg_time)

    if p.level == 0:
        a_plot = ax.scatter(p.x_data, p.y_data,
                            c=p.active_color,
                            s=p.active_point_size)
        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                            c=p.centroid_color,
                            s=p.centroid_point_size)
    elif p.level == 1:
        i_plot = ax.scatter(p.x_data[:p.inactive_idx],
                            p.y_data[:p.inactive_idx],
                            c=p.inactive_color,
                            s=p.inactive_point_size)
        a_plot = ax.scatter(p.x_data[p.inactive_idx:p.d_size],
                            p.y_data[p.inactive_idx:p.d_size],
                            c=p.active_color,
                            s=p.active_point_size)
        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                            c=p.centroid_color,
                            s=p.centroid_point_size)
    elif p.level == 2:
        i_plot_0 = ax.scatter(p.x_data[:p.inactive_idx],
                              p.y_data[:p.inactive_idx],
                              c=p.inactive_color,
                              s=p.inactive_point_size)
        i_plot = ax.scatter(p.x_data[p.inactive_idx + p.s_plus:p.d_size],
                            p.y_data[p.inactive_idx + p.s_plus:p.d_size],
                            c=p.inactive_color,
                            s=p.inactive_point_size)
        a_plot = ax.scatter(p.x_data[p.inactive_idx:p.inactive_idx + p.s_plus],
                            p.y_data[p.inactive_idx:p.inactive_idx + p.s_plus],
                            c=p.active_color,
                            s=p.active_point_size)
        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
                            c=p.centroid_color,
                            s=p.centroid_point_size)

    if p.show_plot_legends == True:

        if p.level == 0:
            leg_plots = ax.legend((a_plot, c_plot),
                                       ('biezacy PP', "controid"),
                                       'upper right', scatterpoints=1)
        else:
            leg_plots = ax.legend((a_plot, i_plot, c_plot),
                            ('biezacy PP', "poprzednie PP", "controid"),
                            'upper right', scatterpoints=1)  # , shadow=True)
        leg_plots.get_frame().set_alpha(0.5)
        ltext = leg_plots.get_texts()
        plt.setp(ltext, fontsize=8)

    savefig(p.frame_file, dpi=p.dpi)
    #print('saving frame: ' + p.frame_file)

    #print('FUNC saving frame: ' + p.frame_file)
    ax.cla()
    fig.clf()
    #plt.close()  # very important line, protects memory leaks
    fig = None
    gc.collect()  # 'to force' garbage collection
    #print('SAVE PNG')
