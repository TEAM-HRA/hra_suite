from pymath.utils.utils import print_import_error
try:
    import os
    import gc
    import multiprocessing
    import pylab as pl
    import matplotlib as mpl
    from matplotlib.pyplot import savefig
    #matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
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


def get_extended_color_array(_color, fill=True):
    """
    method converts _color parameter into extended numpy array
    of colors parts, extended by fourth element which expresses
    """
    if isinstance(_color, ColorRGB):
        return pl.array([_color.red, _color.green, _color.blue,
                         255 if fill else 0]) / 255.0


class PoincarePlotMovieMaker(object):
    """
    class used to generate poincare plot movie
    """
    def __init__(self, data_vector, movie_parameters, **params):
        self.p = movie_parameters
        if not self.p.movie_name == None:
            self.params = Params(**params)
            mpl.rcParams['patch.edgecolor'] = 'none'
            mpl.rcParams['savefig.edgecolor'] = 'none'

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
            self.idx = 0
            self.active_color = get_extended_color_array(
                                        movie_parameters.movie_active_color)
            self.inactive_color = get_extended_color_array(
                                        movie_parameters.movie_inactive_color)
            self.centroid_color = get_extended_color_array(
                                        movie_parameters.movie_centroid_color)
            self.message = None
            self.core_nums = multiprocessing.cpu_count() * self.p.movie_multiprocessing_factor # @IgnorePep8
            self.pp_spec_manager = MiniPoincarePlotSpecManager()
            self.pp_specs_managers = []
            self.pp_specs_managers.append(self.pp_spec_manager)
            self.sub_dir_counter = 0
            self.scatter = None
            self.legend_text = None
            self.pp_specs = []

    def add_data_vector_segment(self, data_vector_segment, last_segment=False):
        self.message = None
        if self.p.movie_name == None:
            return

        if last_segment:
            self.__save_frames__()
            return

        frame_file = as_path(self.p.movie_dir, '%06d.png' % self.idx)
        skip_frame = True if self.idx < self.p.movie_skip_to_frame or \
            (self.p.movie_skip_frames and os.path.exists(frame_file)) \
            else False

        mean_plus = pl.mean(data_vector_segment.signal_plus)
        mean_minus = pl.mean(data_vector_segment.signal_minus)

        s_plus = len(data_vector_segment.signal_plus)

        _p = MiniPoincarePlotSpec()
        _p.idx = self.idx
        _p.s_plus = s_plus
        _p.mean_plus = mean_plus
        _p.mean_minus = mean_minus
        _p.range = self.range
        _p.active_color = self.active_color
        _p.inactive_color = self.inactive_color
        _p.centroid_color = self.centroid_color
        _p.active_point_size = self.p.movie_active_size
        _p.inactive_point_size = self.p.movie_inactive_size
        _p.centroid_point_size = self.p.movie_centroid_size
        _p.frame_file = frame_file
        _p.show_plot_legends = self.p.movie_show_plot_legends

        if self.x_data == None:

            self.x_data = pl.copy(data_vector_segment.signal_plus)
            self.y_data = pl.copy(data_vector_segment.signal_minus)

            ok = True
            old_s_plus = 0
            if skip_frame == False:
                _p.level = 0
                _p.active_start = 0
                _p.active_stop = s_plus
        else:

            old_s_plus = len(self.old_signal_plus)
            ok = False
            if s_plus >= old_s_plus:
                if pl.all(self.old_signal_plus \
                            == data_vector_segment.signal_plus[:old_s_plus]):
                    old_size = len(self.x_data)
                    new_size = old_size + s_plus - old_s_plus
                    _p.active_start = old_size
                    _p.active_stop = new_size

                    self.x_data.resize((new_size), refcheck=False)
                    self.x_data.put(pl.arange(old_size, new_size),
                        data_vector_segment.signal_plus[old_s_plus - s_plus:])

                    self.y_data.resize((new_size), refcheck=False)
                    self.y_data.put(pl.arange(old_size, new_size),
                        data_vector_segment.signal_minus[old_s_plus - s_plus:])

                    if skip_frame == False:
                        _p.level = 1
                    ok = True
                else:
                    for idx in xrange(1, old_s_plus):
                        if pl.all(self.old_signal_plus[idx:] \
                                    == data_vector_segment.signal_plus[idx - 1:
                                                            old_s_plus - idx]):
                            old_size = len(self.x_data)
                            new_size = old_size + s_plus - (old_s_plus - idx)
                            _p.active_start = old_size
                            _p.active_stop = new_size

                            self.x_data.resize((new_size), refcheck=False)
                            self.x_data.put(pl.arange(old_size, new_size),
                                data_vector_segment.signal_plus[
                                                           old_s_plus - idx:])

                            self.y_data.resize((new_size), refcheck=False)
                            self.y_data.put(pl.arange(old_size, new_size),
                                data_vector_segment.signal_minus[
                                                           old_s_plus - idx:])

                            if skip_frame == False:
                                _d = len(self.x_data) - s_plus
                                _p.inactive_start = _d - idx
                                _p.inactive_stop = _d

                                _p.level = 3

                            ok = True
                            break
            else:
                for idx in xrange(1, old_s_plus):
                    if idx + s_plus <= old_s_plus \
                        and pl.all(
                            self.old_signal_plus[idx:idx + s_plus] \
                                    == data_vector_segment.signal_plus):
                        if skip_frame == False:
                            _d = len(self.x_data) - old_s_plus
                            _p.inactive_start = _d
                            _p.inactive_stop = _d + idx

                            if _p.inactive_stop + s_plus < len(self.x_data):
                                _p.inactive_start_2 = _p.inactive_stop + s_plus
                                _p.inactive_stop_2 = len(self.x_data)
                            _p.level = 2

                        ok = True
                        break
        if ok == True and skip_frame == False:
            _p.x_data = self.x_data
            _p.y_data = self.y_data

            if self.p.movie_multiprocessing_factor > 0:
                self.pp_spec_manager.addMiniPoincarePlotSpec(_p)
                if self.idx > 0 and self.idx % self.p.movie_bin_size == 0:
                    if len(self.pp_specs_managers) >= self.core_nums:
                        self.__save_frames__()
                        self.pp_specs_managers = []
                    self.pp_spec_manager = MiniPoincarePlotSpecManager()
                    self.pp_specs_managers.append(self.pp_spec_manager)
            else:
                #self.pp_specs.append(_p)
                create_mini_poincare_plot(_p)
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

    def __save_frames__(self):
        if len(self.pp_specs_managers) > 0:
            pool = multiprocessing.Pool(
                                        processes=self.core_nums
                    #,maxtasksperchild=self.p.movie_multiprocessing_factor
                    )
            pool.map(create_mini_poincare_plot, self.pp_specs_managers,
                    #chunksize=self.p.movie_multiprocessing_factor
                    #chunksize=20
                    )
            pool.close()
            plt.close('all')
            gc.collect()  # 'to force' garbage collection


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
        self.__idx__ = 0
        self.__x_data__ = None
        self.__y_data__ = None
        self.__idx__ = None
        self.__level__ = None
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
        self.__active_start__ = -1
        self.__active_stop__ = -1
        self.__inactive_start__ = -1
        self.__inactive_stop__ = -1
        self.__inactive_start_2__ = -1
        self.__inactive_stop_2__ = -1

    @property
    def idx(self):
        return self.__idx__

    @idx.setter
    def idx(self, _idx):
        self.__idx__ = _idx

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
    def active_start(self):
        return self.__active_start__

    @active_start.setter
    def active_start(self, _active_start):
        self.__active_start__ = _active_start

    @property
    def active_stop(self):
        return self.__active_stop__

    @active_stop.setter
    def active_stop(self, _active_stop):
        self.__active_stop__ = _active_stop

    @property
    def inactive_start(self):
        return self.__inactive_start__

    @inactive_start.setter
    def inactive_start(self, _inactive_start):
        self.__inactive_start__ = _inactive_start

    @property
    def inactive_stop(self):
        return self.__inactive_stop__

    @inactive_stop.setter
    def inactive_stop(self, _inactive_stop):
        self.__inactive_stop__ = _inactive_stop

    @property
    def inactive_start_2(self):
        return self.__inactive_start_2__

    @inactive_start_2.setter
    def inactive_start_2(self, _inactive_start_2):
        self.__inactive_start_2__ = _inactive_start_2

    @property
    def inactive_stop_2(self):
        return self.__inactive_stop_2__

    @inactive_stop_2.setter
    def inactive_stop_2(self, _inactive_stop_2):
        self.__inactive_stop_2__ = _inactive_stop_2

    def __str__(self):
        return ('level: %d, ' +
               ' frame file: %s, active_start %d, active_stop %d, ' +
               ' inactive_start %d, inactive_stop %d, ' +
               ' inactive_start_2 %d, inactive_stop_2 %d '
               ) \
            % (self.level, self.frame_file,
               self.active_start, self.active_stop,
               self.inactive_start, self.inactive_stop,
               self.inactive_start_2, self.inactive_stop_2,
               )


def create_mini_poincare_plot(pp_spec_or_pp_specs_manager):
    #plt.ioff()
    if isinstance(pp_spec_or_pp_specs_manager, MiniPoincarePlotSpecManager):
        pp_specs = pp_spec_or_pp_specs_manager.getMiniPoincarePlotSpecs()
    else:
        pp_specs = [pp_spec_or_pp_specs_manager]

    if len(pp_specs) == 0:
        return

    p0 = pp_specs[0]  # alias
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
    ax.axis(p0.range)
    ax.set_xlabel('$RR_{n}$ [ms]')
    ax.set_ylabel('$RR_{n+1}$ [ms]')
    empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                                edgecolor='none', linewidth=0)

    white = pl.array([255, 255, 255, 0]) / 255.0

    #x_data and y_data are the same for all items included in pp_specs
    #array, we have to add add one item for a centroid value
    x_data = pl.hstack((pl.copy(p0.x_data), pl.array([0])))
    y_data = pl.hstack((pl.copy(p0.y_data), pl.array([0])))

    colors0 = [white] * len(x_data)
    sizes0 = [p0.inactive_point_size] * len(x_data)

    #at the the last index is a centroid
    sizes0[-1] = p0.centroid_point_size
    colors0[-1] = p0.centroid_color

    if p0.level == 0:
        colors0[p0.active_start:p0.active_stop] = \
                [p0.active_color] * (p0.active_stop - p0.active_start)
        sizes0[p0.active_start:p0.active_stop] = \
                [p0.active_point_size] * (p0.active_stop - p0.active_start)
    else:
        if p0.inactive_start >= 0 and p0.inactive_stop >= 0:
            colors0[:p0.inactive_stop] = [p0.inactive_color] * p0.inactive_stop
            sizes0[:p0.inactive_stop] = [p0.inactive_point_size] * p0.inactive_stop # @IgnorePep8
        if p0.active_stop >= 0:
            colors0[p0.inactive_stop:p0.active_stop] = \
                [p0.active_color] * (p0.active_stop - p0.inactive_stop)
            sizes0[p0.inactive_stop:p0.active_stop] = \
                [p0.active_point_size] * (p0.active_stop - p0.inactive_stop)
        if p0.inactive_start_2 >= 0 and p0.inactive_stop_2 >= 0:
            colors0[p0.inactive_start_2:p0.inactive_stop_2] = \
               [p0.inactive_color] * (p0.inactive_stop_2 - p0.inactive_start_2)
            sizes0[p0.inactive_start_2:p0.inactive_stop_2] = \
               [p0.inactive_point_size] * (p0.inactive_stop_2
                                            - p0.inactive_start_2)

    scatter = ax.scatter(x_data, y_data, c=colors0, s=sizes0,
                         edgecolors='none', animated=False)

    sizes = scatter.get_sizes()
    colors = scatter._facecolors
    offsets = scatter.get_offsets()

    if p0.level == 0:
        time_label = get_time_label_for_miliseconds(0)
    else:
        time_label = get_time_label_for_miliseconds(
                                pl.sum(x_data[:p0.inactive_stop]))
    leg_time = ax.legend([empty_rectangle], [time_label], 'upper left')
    leg_time.get_frame().set_alpha(0.5)
    ltext = leg_time.get_texts()
    plt.setp(ltext, fontsize=8)
    ax.add_artist(leg_time)
    legend_text = ltext[0]
    legend_text.set_text(('%s [%d]') % (time_label, p0.idx))

    centroid = pl.array([p0.mean_plus, p0.mean_minus])
    offsets[-1].put(pl.arange(0, 2), centroid)

    fig.savefig(p0.frame_file, dpi=p0.dpi)

    for idx, p in enumerate(pp_specs[1:]):

        if idx % 1000 == 0:
            gc.collect()  # 'to force' garbage collection

        time_label = get_time_label_for_miliseconds(
                                    pl.sum(x_data[:p.inactive_stop]))
        legend_text.set_text(('%s [%d]') % (time_label, p.idx))

        if p.inactive_start >= 0 and p.inactive_stop >= 0:
            sizes[p.inactive_start:p.inactive_stop] = p.inactive_point_size
            colors[p.inactive_start:p.inactive_stop, :] = p.inactive_color

        if p.active_start >= 0 and p.active_stop >= 0:
            sizes[p.active_start:p.active_stop] = p.active_point_size
            colors[p.active_start:p.active_stop, :] = p.active_color

        if p.inactive_start_2 >= 0 and p.inactive_stop_2 >= 0:
            sizes[p.inactive_start_2:p.inactive_stop_2] = p.inactive_point_size
            colors[p.inactive_start_2:p.inactive_stop_2, :] = p.inactive_color

# for future use
#        if p.show_plot_legends == True:
#
#            if p.level == 0:
#                leg_plots = ax.legend((a_plot, c_plot),
#                                       ('biezacy PP', "controid"),
#                                       'upper right', scatterpoints=1)
#            else:
#                leg_plots = ax.legend((a_plot, i_plot, c_plot),
#                            ('biezacy PP', "poprzednie PP", "controid"),
#                            'upper right', scatterpoints=1)  # , shadow=True)
#            leg_plots.get_frame().set_alpha(0.5)
#            ltext = leg_plots.get_texts()
#            plt.setp(ltext, fontsize=8)

        #set up a controid value
        centroid = pl.array([p.mean_plus, p.mean_minus])
        offsets[-1].put(pl.arange(0, 2), centroid)

        fig.savefig(p.frame_file, dpi=p.dpi)

    ax.cla()
    fig.clf()
    #plt.close()  # very important line, protects memory leaks
    fig = None
    #plt.close('all')
    #plt = None
    gc.collect()  # 'to force' garbage collection
    #print('SAVE PNG')


#OLD VERSION
#def create_mini_poincare_plot_v0(pp_spec):
#    #print('IN create_mini_poincare_plot')
#    #plt.ioff()
#    p = pp_spec  # alias
#    fig = plt.figure()
#    ax = fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
#    ax.axis(p.range)
#    ax.set_xlabel('$RR_{n}$ [ms]')
#    ax.set_ylabel('$RR_{n+1}$ [ms]')
#    empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
#                                edgecolor='none', linewidth=0)
#    if p.level == 0:
#        time_label = get_time_label_for_miliseconds(0)
#    else:
#        time_label = get_time_label_for_miliseconds(
#                                pl.sum(p.x_data[:p.inactive_idx]))
#    leg_time = ax.legend([empty_rectangle], [time_label],
#                          'upper left')
#    leg_time.get_frame().set_alpha(0.5)
#    ltext = leg_time.get_texts()
#    plt.setp(ltext, fontsize=8)
#    ax.add_artist(leg_time)
#
#    if p.level == 0:
#        a_plot = ax.scatter(p.x_data, p.y_data,
#                            c=p.active_color,
#                            s=p.active_point_size)
#        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
#                            c=p.centroid_color,
#                            s=p.centroid_point_size)
#    elif p.level == 1:
#        i_plot = ax.scatter(p.x_data[:p.inactive_idx],
#                            p.y_data[:p.inactive_idx],
#                            c=p.inactive_color,
#                            s=p.inactive_point_size)
#        a_plot = ax.scatter(p.x_data[p.inactive_idx:p.d_size],
#                            p.y_data[p.inactive_idx:p.d_size],
#                            c=p.active_color,
#                            s=p.active_point_size)
#        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
#                            c=p.centroid_color,
#                            s=p.centroid_point_size)
#    elif p.level == 2:
#        i_plot_0 = ax.scatter(p.x_data[:p.inactive_idx],
#                              p.y_data[:p.inactive_idx],
#                              c=p.inactive_color,
#                              s=p.inactive_point_size)
#        i_plot = ax.scatter(p.x_data[p.inactive_idx + p.s_plus:p.d_size],
#                            p.y_data[p.inactive_idx + p.s_plus:p.d_size],
#                            c=p.inactive_color,
#                            s=p.inactive_point_size)
#       a_plot = ax.scatter(p.x_data[p.inactive_idx:p.inactive_idx + p.s_plus],
#                           p.y_data[p.inactive_idx:p.inactive_idx + p.s_plus],
#                            c=p.active_color,
#                            s=p.active_point_size)
#        c_plot = ax.scatter([p.mean_plus], [p.mean_minus],
#                            c=p.centroid_color,
#                            s=p.centroid_point_size)
#
#    if p.show_plot_legends == True:
#
#        if p.level == 0:
#            leg_plots = ax.legend((a_plot, c_plot),
#                                       ('biezacy PP', "controid"),
#                                       'upper right', scatterpoints=1)
#        else:
#            leg_plots = ax.legend((a_plot, i_plot, c_plot),
#                            ('biezacy PP', "poprzednie PP", "controid"),
#                            'upper right', scatterpoints=1)  # , shadow=True)
#        leg_plots.get_frame().set_alpha(0.5)
#        ltext = leg_plots.get_texts()
#        plt.setp(ltext, fontsize=8)
#
#    savefig(p.frame_file, dpi=p.dpi)
#    #print('saving frame: ' + p.frame_file)
#
#    #print('FUNC saving frame: ' + p.frame_file)
#    ax.cla()
#    fig.clf()
#    #plt.close()  # very important line, protects memory leaks
#    fig = None
#    gc.collect()  # 'to force' garbage collection
#    #print('SAVE PNG')
