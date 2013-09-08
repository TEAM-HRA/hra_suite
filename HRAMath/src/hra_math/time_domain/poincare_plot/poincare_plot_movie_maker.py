from hra_math.utils.utils import print_import_error
try:
    import os
    import gc
    import multiprocessing
    import pylab as pl
    import matplotlib as mpl
    #matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from hra_core.misc import Params
    from hra_core.misc import ColorRGB
    from hra_core.io_utils import as_path
    from hra_math.time_domain.poincare_plot.poincare_plot_animation \
                                    import PoincarePlotAnimation
    from hra_math.time_domain.poincare_plot.poincare_plot_movie_worker \
                                    import PoincarePlotMovieMakerWorker
    from hra_math.time_domain.poincare_plot.poincare_plot_fast_movie_worker \
                                    import PoincarePlotFastMovieMakerWorker
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
            self.signal_size = len(data_vector.signal)
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
            self.pp_spec_manager.movie_dir = self.p.movie_dir
            self.pp_spec_manager.movie_name = self.p.movie_name
            self.pp_spec_manager.movie_dpi = self.p.movie_dpi
            self.pp_spec_manager.movie_fps = self.p.movie_fps

            self.pp_specs_managers = []
            self.pp_specs_managers.append(self.pp_spec_manager)
            self.sub_dir_counter = 0
            self.scatter = None
            self.legend_text = None
            self.pp_specs = []
            self.cum_inactive = 0
            self._p_old = None

    def add_data_vector_segment(self, data_vector_segment, last_segment=False):
        self.message = None
        if self.p.movie_name == None:
            return

        if last_segment:
            self.__save_frames__()
            return

        frame_name = '%06d' % self.idx
        frame_file = as_path(self.p.movie_dir, frame_name + '.png')
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
                    if new_size > old_size:
                        _p.active_start = old_size
                        _p.active_stop = new_size

                        self.x_data.resize((new_size), refcheck=False)
                        self.x_data.put(pl.arange(old_size, new_size),
                            data_vector_segment.signal_plus[old_s_plus
                                                            - s_plus:])

                        self.y_data.resize((new_size), refcheck=False)
                        self.y_data.put(pl.arange(old_size, new_size),
                            data_vector_segment.signal_minus[old_s_plus
                                                             - s_plus:])

                        _p.inactive_stop = self._p_old.inactive_stop
                    _p.level = 1
                    ok = True
                else:
                    for idx in xrange(1, old_s_plus):
                        if pl.all(self.old_signal_plus[idx:] \
                                    == data_vector_segment.signal_plus[idx - 1:
                                                            old_s_plus - idx]):
                            old_size = len(self.x_data)
                            new_size = old_size + s_plus - (old_s_plus - idx)

                            if new_size > old_size:
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
            _p.cum_inactive = self.cum_inactive
            #print('PP_SPEC: ' + str(_p))

            self.pp_spec_manager.addMiniPoincarePlotSpec(_p)
            if self.idx > 0 and \
                (self.p.movie_bin_size > 0
                    and ((self.idx % self.p.movie_bin_size) == 0)):
                if len(self.pp_specs_managers) >= self.core_nums:
                    if self.p.movie_calculate_all_frames == False:
                        self.__save_frames__()
                        self.pp_specs_managers = []

                old_pp_spec_manager = self.pp_spec_manager
                self.pp_spec_manager = MiniPoincarePlotSpecManager()
                self.pp_spec_manager.movie_dir = self.p.movie_dir
                self.pp_spec_manager.movie_name = self.p.movie_name
                self.pp_spec_manager.movie_dpi = self.p.movie_dpi
                self.pp_spec_manager.movie_fps = self.p.movie_fps
                self.pp_spec_manager.previous_manager = old_pp_spec_manager

                self.pp_specs_managers.append(self.pp_spec_manager)
            self.message = 'Prepare frame: %s' % (frame_name)
        elif ok == True and skip_frame == True:
            self.message = 'Skip frame %s' % (frame_name)
        elif ok == False:
            print('s_plus: ' + str(s_plus) + ' old_s_plus: ' + str(old_s_plus))
            print('old_signal_plus: ' + str(self.old_signal_plus))
            print('signal_plus:     ' + str(data_vector_segment.signal_plus))
            raise Exception('Error for idx ' + str(self.idx))
        if _p.inactive_start >= 0 and _p.inactive_stop >= 0:
            self.cum_inactive += pl.sum(
                            self.x_data[_p.inactive_start:_p.inactive_stop])

        self.old_signal_plus = data_vector_segment.signal_plus
        self.idx = self.idx + 1
        self._p_old = _p

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
            if self.p.movie_multiprocessing_factor > 0:
                pool = multiprocessing.Pool(processes=self.core_nums
                    #,maxtasksperchild=self.p.movie_multiprocessing_factor
                    )
                if not self.params.info_message_handler == None:
                    self.params.info_message_handler('Generating frames'
                                                 + (' ' * 20))
                pool.map(self.__poincare_plot_function__,
                         self.pp_specs_managers,
                         #chunksize=self.p.movie_multiprocessing_factor
                         #chunksize=20
                         )
                pool.close()
            else:
                _function = self.__poincare_plot_function__
                for pp_spec_manager in self.pp_specs_managers:
                    _function(pp_spec_manager)

    @property
    def __poincare_plot_function__(self):
        if self.p.movie_animated:
            return create_animated_mini_poincare_plot
        elif self.p.movie_experimental_code:
            return create_mini_poincare_plot_experimental
        else:
            return create_mini_poincare_plot


class MiniPoincarePlotSpecManager(object):
    """
    class used to collect MiniPoincarePlotSpec objects,
    the class is introduced because of multiprocesing pool functionality,
    the method Pool.map doesn't work if an iterable parameter contains
    subarrays it have to be usual not iterable objects
    """
    def __init__(self):
        self.__pp_specs__ = []
        self.__movie_dir__ = None
        self.__movie_name__ = None
        self.__movie_fps__ = None
        self.__movie_dpi__ = None
        self.__previous_manager__ = None

    def addMiniPoincarePlotSpec(self, pp_spec):
        self.__pp_specs__.append(pp_spec)

    def getMiniPoincarePlotSpecs(self):
        return self.__pp_specs__

    @property
    def movie_dir(self):
        return self.__movie_dir__

    @movie_dir.setter
    def movie_dir(self, _movie_dir):
        self.__movie_dir__ = _movie_dir

    @property
    def movie_name(self):
        return self.__movie_name__

    @movie_name.setter
    def movie_name(self, _movie_name):
        self.__movie_name__ = _movie_name

    @property
    def movie_fps(self):
        return self.__movie_fps__

    @movie_fps.setter
    def movie_fps(self, _movie_fps):
        self.__movie_fps__ = _movie_fps

    @property
    def movie_dpi(self):
        return self.__movie_dpi__

    @movie_dpi.setter
    def movie_dpi(self, _movie_dpi):
        self.__movie_dpi__ = _movie_dpi

    @property
    def previous_manager(self):
        return self.__previous_manager__

    @previous_manager.setter
    def previous_manager(self, _previous_manager):
        self.__previous_manager__ = _previous_manager


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
        self.__cum_inactive__ = 0

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

    @property
    def cum_inactive(self):
        return self.__cum_inactive__

    @cum_inactive.setter
    def cum_inactive(self, _cum_inactive):
        self.__cum_inactive__ = _cum_inactive

    def __str__(self):
        return ('level: %d, ' +
               ' frame file: %s, active_start %d, active_stop %d, ' +
               ' inactive_start %d, inactive_stop %d, ' +
               ' inactive_start_2 %d, inactive_stop_2 %d, cum_inactive %d '
               ) \
            % (self.level, self.frame_file,
               self.active_start, self.active_stop,
               self.inactive_start, self.inactive_stop,
               self.inactive_start_2, self.inactive_stop_2, self.cum_inactive
               )


def create_mini_poincare_plot(pp_spec_or_pp_specs_manager):
    movie_maker = PoincarePlotMovieMakerWorker(pp_spec_or_pp_specs_manager)
    if movie_maker.initiate():
        movie_maker.fig.savefig(movie_maker.p0.frame_file,
                                dpi=movie_maker.p0.dpi)
        for idx, p in enumerate(movie_maker.pp_specs[1:]):
            movie_maker.plot(idx)
            movie_maker.fig.savefig(p.frame_file, dpi=p.dpi)
        plt.close('all')
        gc.collect()  # 'to force' garbage collection


def create_animated_mini_poincare_plot(pp_specs_manager):
    PoincarePlotAnimation(pp_specs_manager)
    plt.close('all')
    gc.collect()  # 'to force' garbage collection


def create_mini_poincare_plot_experimental(pp_specs_manager):
    #print('\nWarning !! Experimental code ! Not implemented !\n')
    print('\nWarning !! Experimental code !\n')
    movie_worker = PoincarePlotFastMovieMakerWorker(pp_specs_manager)
    if movie_worker.initiate():
        for idx, _ in enumerate(movie_worker.pp_specs[1:]):
            movie_worker.plot(idx)
        gc.collect()
