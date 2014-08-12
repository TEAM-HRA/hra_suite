from hra_math.utils.utils import print_import_error
try:
    import gc
    import multiprocessing
    import pylab as pl
    import matplotlib as mpl
    #matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from hra_core.misc import Params
    from hra_core.misc import ColorRGB
    from hra_core.misc import is_empty
    from hra_core.io_utils import as_path
    from hra_core.io_utils import create_dir
    from hra_core.io_utils import get_filename
    from hra_core.movie_utils import generate_movie
    from hra_core.collections_utils import get_chunks
    from hra_core.collections_utils import nvl
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
            self.source = get_filename(self.params.reference_filename)
            self.__prefixed_movie_name__ = self.__get_prefixed_movie_name__()
            self.__prefixed_movie_dir__ = self.__get_prefixed_movie_dir__()

            if not self.params.filter_manager == None:
                data_vector = self.params.filter_manager.run_filters(
                                                                data_vector)
            _max = pl.amax(data_vector.signal)
            _min = pl.amin(data_vector.signal)
            self.time = data_vector.time

            margin = 50
            self.signal_size = len(data_vector.signal)
            self.range = [_min - margin, _max + margin,
                          _min - margin, _max + margin]
            self.x_data = pl.zeros(self.signal_size)
            self.y_data = pl.zeros(self.signal_size)

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
            self.pp_spec_manager.movie_dir = self.__prefixed_movie_dir__
            self.pp_spec_manager.movie_name = self.__prefixed_movie_name__
            self.pp_spec_manager.movie_dpi = self.p.movie_dpi
            self.pp_spec_manager.movie_fps = self.p.movie_fps
            self.pp_spec_manager.movie_height = self.p.movie_height
            self.pp_spec_manager.movie_width = self.p.movie_width
            self.pp_spec_manager.active_color = self.active_color
            self.pp_spec_manager.inactive_color = self.inactive_color
            self.pp_spec_manager.centroid_color = self.centroid_color
            self.pp_spec_manager.active_point_size = self.p.movie_active_size
            self.pp_spec_manager.inactive_point_size = \
                                            self.p.movie_inactive_size
            self.pp_spec_manager.centroid_point_size = \
                                            self.p.movie_centroid_size
            self.pp_spec_manager.show_plot_legends = \
                                        self.p.movie_show_plot_legends
            self.pp_spec_manager.x_label = self.p.x_label
            self.pp_spec_manager.y_label = self.p.y_label
            self.pp_spec_manager.clean_frames = self.p.movie_clean_frames
            self.pp_spec_manager.movie_title = self.p.movie_title
            self.pp_spec_manager.movie_frame_step = self.p.movie_frame_step
            self.pp_spec_manager.movie_identity_line = self.p.movie_identity_line
            self.pp_spec_manager.movie_hour_label = self.p.movie_hour_label
            self.pp_spec_manager.movie_minute_label = self.p.movie_minute_label
            self.pp_spec_manager.movie_second_label = self.p.movie_second_label
            self.pp_spec_manager.movie_time_label_in_line = self.p.movie_time_label_in_line
            self.pp_spec_manager.movie_time_label_font_size = self.p.movie_time_label_font_size
            self.pp_spec_manager.movie_time_label_prefix = self.p.movie_time_label_prefix
            self.pp_spec_manager.movie_title_font_size = self.p.movie_title_font_size
            self.pp_spec_manager.movie_axis_font_size = self.p.movie_axis_font_size
            self.pp_spec_manager.movie_axis_font = self.p.movie_axis_font
            self.pp_spec_manager.movie_title_font = self.p.movie_title_font
            self.pp_spec_manager.movie_tick_font = self.p.movie_tick_font
            self.pp_spec_manager.movie_frame_pad = self.p.movie_frame_pad

            self.pp_specs_managers = []
            self.pp_specs_managers.append(self.pp_spec_manager)
            self.sub_dir_counter = 0
            self.scatter = None
            self.legend_text = None
            self.pp_specs = []
            self.cum_inactive = 0
            self._pp_spec_old = None
            self.s_size = 0  # current calculated signal size

    def add_data_vector_segment(self, data_vector_segment, last_segment=False):
        self.message = None
        if self.__prefixed_movie_name__ == None:
            return

        if last_segment:
            self.__save_frames__()
            return

        frame_name = '%s_%06d' % (self.__prefixed_movie_name__, self.idx)
        frame_file = as_path(self.__prefixed_movie_dir__, frame_name + '.png')
        #skip_frame = True if self.idx < self.p.movie_skip_to_frame or \
        #    (self.p.movie_skip_frames and os.path.exists(frame_file)) \
        #    else False
        skip_frame = False

        mean_plus = pl.mean(data_vector_segment.signal_plus)
        mean_minus = pl.mean(data_vector_segment.signal_minus)

        s_plus = len(data_vector_segment.signal_plus)

        _pp_spec = MiniPoincarePlotSpec()
        _pp_spec.idx = self.idx
        _pp_spec.s_plus = s_plus
        _pp_spec.mean_plus = mean_plus
        _pp_spec.mean_minus = mean_minus
        _pp_spec.range = self.range
        _pp_spec.frame_file = frame_file

        if self.idx == 0:

            self.s_size = s_plus
            self.x_data.put(pl.arange(s_plus), data_vector_segment.signal_plus)
            self.y_data.put(pl.arange(s_plus),
                                            data_vector_segment.signal_minus)

            ok = True
            old_s_plus = 0
            _pp_spec.level = 0
            _pp_spec.active_start = 0
            _pp_spec.active_stop = s_plus
        else:
            old_s_plus = len(self.old_signal_plus)
            ok = False
            if s_plus >= old_s_plus:
                if pl.all(self.old_signal_plus \
                            == data_vector_segment.signal_plus[:old_s_plus]):
                    old_size = self.s_size
                    new_size = old_size + s_plus - old_s_plus
                    if new_size > old_size:
                        _pp_spec.active_start = old_size
                        _pp_spec.active_stop = new_size

                        if new_size > len(self.x_data):
                            raise Exception(
                                'New size is greater then the signal size !')

                        self.x_data.put(pl.arange(old_size, new_size),
                            data_vector_segment.signal_plus[old_s_plus
                                                            - s_plus:])

                        self.y_data.put(pl.arange(old_size, new_size),
                            data_vector_segment.signal_minus[old_s_plus
                                                             - s_plus:])

                        _pp_spec.inactive_stop = \
                                        self._pp_spec_old.inactive_stop
                        self.s_size = new_size
                    _pp_spec.level = 1
                    ok = True
                else:
                    for idx in xrange(1, old_s_plus):
                        if pl.all(self.old_signal_plus[idx:] \
                                    == data_vector_segment.signal_plus[idx - 1:
                                                            old_s_plus - idx]):
                            old_size = self.s_size
                            new_size = old_size + s_plus - (old_s_plus - idx)

                            if new_size > len(self.x_data):
                                raise Exception(
                                'New size is greater then the signal size !')

                            if new_size > old_size:
                                _pp_spec.active_start = old_size
                                _pp_spec.active_stop = new_size

                                self.x_data.put(pl.arange(old_size, new_size),
                                    data_vector_segment.signal_plus[
                                                           old_s_plus - idx:])

                                self.y_data.put(pl.arange(old_size, new_size),
                                    data_vector_segment.signal_minus[
                                                           old_s_plus - idx:])
                                self.s_size = new_size

                            _d = self.s_size - s_plus
                            _pp_spec.inactive_start = _d - idx
                            _pp_spec.inactive_stop = _d

                            _pp_spec.level = 3

                            ok = True
                            break
            else:
                for idx in xrange(1, old_s_plus):
                    if idx + s_plus <= old_s_plus \
                        and pl.all(
                            self.old_signal_plus[idx:idx + s_plus] \
                                    == data_vector_segment.signal_plus):

                        _d = self.s_size - old_s_plus
                        _pp_spec.inactive_start = _d
                        _pp_spec.inactive_stop = _d + idx

                        if _pp_spec.inactive_stop + s_plus < self.s_size:
                            _pp_spec.inactive_start_2 = \
                                        _pp_spec.inactive_stop + s_plus
                            _pp_spec.inactive_stop_2 = self.s_size
                        _pp_spec.level = 2

                        ok = True
                        break
        if ok == True and skip_frame == False:
            _pp_spec.x_data = self.x_data
            _pp_spec.y_data = self.y_data
            _pp_spec.cum_inactive = self.cum_inactive
            _pp_spec.s_size = self.s_size
            #print('PP_SPEC: ' + str(_p))

            self.pp_spec_manager.addMiniPoincarePlotSpec(_pp_spec)
            if self.idx > 0 and \
                (self.p.movie_bin_size > 0
                    and ((self.idx % self.p.movie_bin_size) == 0)):
                if len(self.pp_specs_managers) >= self.core_nums:
                    if self.p.movie_calculate_all_frames == False:
                        self.__save_frames__()
                        self.pp_specs_managers = []

                old_pp_spec_manager = self.pp_spec_manager
                self.pp_spec_manager = MiniPoincarePlotSpecManager()
                self.pp_spec_manager.movie_dir = self.__prefixed_movie_dir__
                self.pp_spec_manager.movie_name = self.__prefixed_movie_name__
                self.pp_spec_manager.movie_dpi = self.p.movie_dpi
                self.pp_spec_manager.movie_fps = self.p.movie_fps
                self.pp_spec_manager.movie_height = self.p.movie_height
                self.pp_spec_manager.movie_width = self.p.movie_width
                self.pp_spec_manager.active_color = self.active_color
                self.pp_spec_manager.inactive_color = self.inactive_color
                self.pp_spec_manager.centroid_color = self.centroid_color
                self.pp_spec_manager.active_point_size = \
                                                self.p.movie_active_size
                self.pp_spec_manager.inactive_point_size = \
                                                self.p.movie_inactive_size
                self.pp_spec_manager.centroid_point_size = \
                                                self.p.movie_centroid_size
                self.pp_spec_manager.show_plot_legends = \
                                            self.p.movie_show_plot_legends
                self.pp_spec_manager.x_label = self.p.x_label
                self.pp_spec_manager.y_label = self.p.y_label
                self.pp_spec_manager.clean_frames = self.p.movie_clean_frames
                self.pp_spec_manager.movie_title = self.p.movie_title
                self.pp_spec_manager.movie_frame_step = self.p.movie_frame_step
                self.pp_spec_manager.movie_identity_line = self.p.movie_identity_line
                self.pp_spec_manager.movie_hour_label = self.p.movie_hour_label
                self.pp_spec_manager.movie_minute_label = self.p.movie_minute_label
                self.pp_spec_manager.movie_second_label = self.p.movie_second_label
                self.pp_spec_manager.movie_time_label_in_line = self.p.movie_time_label_in_line
                self.pp_spec_manager.movie_time_label_font_size = self.p.movie_time_label_font_size
                self.pp_spec_manager.movie_time_label_prefix = self.p.movie_time_label_prefix
                self.pp_spec_manager.movie_title_font_size = self.p.movie_title_font_size
                self.pp_spec_manager.movie_axis_font_size = self.p.movie_axis_font_size
                self.pp_spec_manager.movie_axis_font = self.p.movie_axis_font
                self.pp_spec_manager.movie_title_font = self.p.movie_title_font
                self.pp_spec_manager.movie_tick_font = self.p.movie_tick_font
                self.pp_spec_manager.movie_frame_pad = self.p.movie_frame_pad                

                #add all previous pp specs
                for pp_spec in old_pp_spec_manager.getMiniPoincarePlotSpecs():
                    self.pp_spec_manager.addPreviousPoincarePlotSpecMinimum(
                                                                    pp_spec)
                old_pp_spec_manager = None

                self.pp_specs_managers.append(self.pp_spec_manager)
            self.message = 'Prepare frame: %s' % (frame_name)
        elif ok == True and skip_frame == True:
            self.message = 'Skip frame %s' % (frame_name)
        elif ok == False:
            print('s_plus: ' + str(s_plus) + ' old_s_plus: ' + str(old_s_plus))
            print('old_signal_plus: ' + str(self.old_signal_plus))
            print('signal_plus:     ' + str(data_vector_segment.signal_plus))
            raise Exception('Error for idx ' + str(self.idx))
        if _pp_spec.inactive_start >= 0 and _pp_spec.inactive_stop >= 0:
            #if time array is not None use it as array for cumulative time
            if not self.time == None:
                self.cum_inactive += pl.sum(
                    self.time[
                            _pp_spec.inactive_start:_pp_spec.inactive_stop])
            else:
                self.cum_inactive += pl.sum(
                    self.x_data[
                            _pp_spec.inactive_start:_pp_spec.inactive_stop])

        self.old_signal_plus = data_vector_segment.signal_plus
        self.idx = self.idx + 1
        self._pp_spec_old = _pp_spec

        #gc.collect()  # this invocation slow down process of movie generation

    def save_movie(self):
        if not self.__prefixed_movie_name__ == None and self.p.movie_not_save == False:  # @IgnorePep8

            output_file = generate_movie(self.__prefixed_movie_name__,
                                    self.__prefixed_movie_dir__,
                                    self.p.movie_width, self.p.movie_height,
                                    self.p.movie_fps,
                                    movie_clean_frames=self.p.movie_clean_frames)
            self.message = "Poincare plot movie %s is created !" \
                            % as_path(self.__prefixed_movie_dir__, output_file)

    @property
    def info_message(self):
        return self.message

    def __save_frames__(self):
        size = len(self.pp_specs_managers)
        if size > 0:
            #create output movie dir if it is not present
            create_dir(self.pp_specs_managers[0].movie_dir)

            if self.p.movie_multiprocessing_factor > 0:
                for specs_managers in get_chunks(self.pp_specs_managers,
                                                 self.core_nums):
                    pool = multiprocessing.Pool(processes=self.core_nums
                        #,maxtasksperchild=self.p.movie_multiprocessing_factor
                        )
                    if not self.params.info_message_handler == None:
                        self.params.info_message_handler('Generating frames'
                                                     + (' ' * 20))
                    pool.map(self.__poincare_plot_function__,
                             specs_managers,
                             #self.pp_specs_managers,
                             #chunksize=self.p.movie_multiprocessing_factor
                             #chunksize=20
                             )
                    pool.close()
                    gc.collect()
            else:
                _function = self.__poincare_plot_function__
                for pp_spec_manager in self.pp_specs_managers:
                    _function(pp_spec_manager)

    @property
    def __poincare_plot_function__(self):
        if self.p.movie_animated:
            return create_mini_poincare_plot_animated_generation
        elif self.p.movie_standard_generation:
            return create_mini_poincare_plot_standard_generation
        elif self.p.movie_experimental_code:
            return create_mini_poincare_plot_experimental
        else:
            #the default choice
            return create_mini_poincare_plot_fast_generation

    def __get_prefixed_movie_name__(self):
        """
        method prefixed movie_name by source name and output_prefix
        """
        movie_name = self.p.movie_name

        #append source filename
        movie_name = '%s_%s' % (self.source, movie_name) \
                if self.p.movie_prefixed_by_source else movie_name

        #append output_prefix
        return movie_name if is_empty(self.p.output_prefix) \
                        else '%s_%s' % (self.p.output_prefix, movie_name)

    def __get_prefixed_movie_dir__(self):
        """
        method returns prefixed movie_dir by source name and output_prefix
        """
        movie_dir = self.p.movie_dir

        prefix = self.p.output_prefix + '_' \
                if not is_empty(self.p.output_prefix) else ''

        return as_path(movie_dir, prefix + 'm_' + self.source) \
                if self.p.movie_prefixed_by_source else movie_dir


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
        self.__previous_pp_specs__ = []
        self.__active_color__ = None
        self.__inactive_color__ = None
        self.__centroid_color__ = None
        self.__active_point_size__ = None
        self.__inactive_point_size__ = None
        self.__centroid_point_size__ = None
        self.__show_plot_legends__ = False
        self.__movie_width__ = None
        self.__movie_height__ = None
        self.__x_label__ = None
        self.__y_label__ = None
        self.__clean_frames__ = True
        self.__movie_title__ = None
        self.__movie_frame_step__ = None
        self.__movie_hour_label__ = None
        self.__movie_minute_label__ = None
        self.__movie_second_label__ = None
        self.__movie_time_label_in_line__ = None
        self.__movie_time_label_font_size__ = None
        self.__movie_time_label_prefix__ = None
        self.__movie_title_font_size__ = None
        self.__movie_axis_font_size__ = None
        self.__movie_axis_font__ = None
        self.__movie_title_font__ = None
        self.__movie_tick_font__ = None
        self.__movie_frame_pad__ = None

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
        return nvl(self.__movie_dpi__, 70)

    @movie_dpi.setter
    def movie_dpi(self, _movie_dpi):
        self.__movie_dpi__ = _movie_dpi

    @property
    def active_color(self):
        return self.__active_color__

    @active_color.setter
    def active_color(self, _active_color):
        self.__active_color__ = _active_color

    @property
    def active_color_as_tuple(self):
        return self.__color_as_tuple__(self.__active_color__)

    @property
    def inactive_color(self):
        return self.__inactive_color__

    @inactive_color.setter
    def inactive_color(self, _inactive_color):
        self.__inactive_color__ = _inactive_color

    @property
    def inactive_color_as_tuple(self):
        return self.__color_as_tuple__(self.__inactive_color__)

    @property
    def centroid_color(self):
        return self.__centroid_color__

    @property
    def centroid_color_as_tuple(self):
        return self.__color_as_tuple__(self.__centroid_color__)

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
    def show_plot_legends(self):
        return self.__show_plot_legends__

    @show_plot_legends.setter
    def show_plot_legends(self, _show_plot_legends):
        self.__show_plot_legends__ = _show_plot_legends

    @property
    def movie_width(self):
        return self.__movie_width__

    @movie_width.setter
    def movie_width(self, _movie_width):
        self.__movie_width__ = _movie_width

    @property
    def movie_height(self):
        return self.__movie_height__

    @movie_height.setter
    def movie_height(self, _movie_height):
        self.__movie_height__ = _movie_height

    @property
    def x_label(self):
        return self.__x_label__

    @x_label.setter
    def x_label(self, _x_label):
        self.__x_label__ = _x_label

    @property
    def y_label(self):
        return self.__y_label__

    @y_label.setter
    def y_label(self, _y_label):
        self.__y_label__ = _y_label

    @property
    def clean_frames(self):
        return self.__clean_frames__

    @clean_frames.setter
    def clean_frames(self, _clean_frames):
        self.__clean_frames__ = _clean_frames

    @property
    def movie_title(self):
        return self.__movie_title__

    @movie_title.setter
    def movie_title(self, _movie_title):
        self.__movie_title__ = _movie_title

    @property
    def movie_hour_label(self):
        return self.__movie_hour_label__

    @movie_hour_label.setter
    def movie_hour_label(self, _movie_hour_label):
        self.__movie_hour_label__ = _movie_hour_label

    @property
    def movie_minute_label(self):
        return self.__movie_minute_label__

    @movie_minute_label.setter
    def movie_minute_label(self, _movie_minute_label):
        self.__movie_minute_label__ = _movie_minute_label

    @property
    def movie_second_label(self):
        return self.__movie_second_label__

    @movie_second_label.setter
    def movie_second_label(self, _movie_second_label):
        self.__movie_second_label__ = _movie_second_label

    @property
    def movie_time_label_in_line(self):
        return self.__movie_time_label_in_line__

    @movie_time_label_in_line.setter
    def movie_time_label_in_line(self, _movie_time_label_in_line):
        self.__movie_time_label_in_line__ = _movie_time_label_in_line

    @property
    def movie_time_label_font_size(self):
        return self.__movie_time_label_font_size__

    @movie_time_label_font_size.setter
    def movie_time_label_font_size(self, _movie_time_label_font_size):
        self.__movie_time_label_font_size__ = _movie_time_label_font_size

    @property
    def movie_time_label_prefix(self):
        return self.__movie_time_label_prefix__

    @movie_time_label_prefix.setter
    def movie_time_label_prefix(self, _movie_time_label_prefix):
        self.__movie_time_label_prefix__ = _movie_time_label_prefix

    @property
    def movie_title_font_size(self):
        return self.__movie_title_font_size__

    @movie_title_font_size.setter
    def movie_title_font_size(self, _movie_title_font_size):
        self.__movie_title_font_size__ = _movie_title_font_size

    @property
    def movie_axis_font_size(self):
        return self.__movie_axis_font_size__

    @movie_axis_font_size.setter
    def movie_axis_font_size(self, _movie_axis_font_size):
        self.__movie_axis_font_size__ = _movie_axis_font_size

    @property
    def movie_axis_font(self):
        return self.__movie_axis_font__

    @movie_axis_font.setter
    def movie_axis_font(self, _movie_axis_font):
        self.__movie_axis_font__ = _movie_axis_font

    @property
    def movie_title_font(self):
        return self.__movie_title_font__

    @movie_title_font.setter
    def movie_title_font(self, _movie_title_font):
        self.__movie_title_font__ = _movie_title_font

    @property
    def movie_tick_font(self):
        return self.__movie_tick_font__

    @movie_tick_font.setter
    def movie_tick_font(self, _movie_tick_font):
        self.__movie_tick_font__ = _movie_tick_font

    @property
    def movie_frame_pad(self):
        return self.__movie_frame_pad__

    @movie_frame_pad.setter
    def movie_frame_pad(self, _movie_frame_pad):
        self.__movie_frame_pad__ = _movie_frame_pad

    def __color_as_tuple__(self, _color):
        _c = _color
        return (_c[0], _c[1], _c[2], 1.0) if not _c == None else None

    def addPreviousPoincarePlotSpecMinimum(self, pp_spec):
        p = pp_spec  # alias
        self.__previous_pp_specs__.append(
                MiniPoincarePlotSpecMinimum(level=p.level,
                                        active_start=p.active_start,
                                        active_stop=p.active_stop,
                                        inactive_start=p.inactive_start,
                                        inactive_stop=p.inactive_stop,
                                        inactive_start_2=p.inactive_start_2,
                                        inactive_stop_2=p.inactive_stop_2))

    def getPreviousPoincarePlotSpecsMinimum(self):
        return self.__previous_pp_specs__


class MiniPoincarePlotSpecMinimum(object):
    """
    class used to store some important properties of mini-poincare plot
    """

    def __init__(self, **kvarg):
        self.__level__ = kvarg.get('level', None)
        self.__active_start__ = kvarg.get('active_start', -1)
        self.__active_stop__ = kvarg.get('active_stop', -1)
        self.__inactive_start__ = kvarg.get('inactive_start', -1)
        self.__inactive_stop__ = kvarg.get('inactive_stop', -1)
        self.__inactive_start_2__ = kvarg.get('inactive_start_2', -1)
        self.__inactive_stop_2__ = kvarg.get('inactive_stop_2', -1)

    @property
    def level(self):
        return self.__level__

    @level.setter
    def level(self, _level):
        self.__level__ = _level

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
        return ('level: %d,  ' +
               ' active_start %d, active_stop %d, ' +
               ' inactive_start %d, inactive_stop %d, ' +
               ' inactive_start_2 %d, inactive_stop_2 %d '
               ) \
            % (self.level,
               self.active_start, self.active_stop,
               self.inactive_start, self.inactive_stop,
               self.inactive_start_2, self.inactive_stop_2)


class MiniPoincarePlotSpec(MiniPoincarePlotSpecMinimum):
    """
    class used to store some important properties of mini-poincare plot
    """

    def __init__(self):
        super(MiniPoincarePlotSpec, self).__init__()
        self.__idx__ = 0
        self.__x_data__ = None
        self.__y_data__ = None
        self.__idx__ = None
        self.__mean_plus__ = None
        self.__mean_minus__ = None
        self.__range__ = None
        self.__frame_file__ = None
        self.__cum_inactive__ = 0
        self.__s_size__ = 0

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
    def frame_file(self):
        return self.__frame_file__

    @frame_file.setter
    def frame_file(self, _frame_file):
        self.__frame_file__ = _frame_file

    @property
    def cum_inactive(self):
        return self.__cum_inactive__

    @cum_inactive.setter
    def cum_inactive(self, _cum_inactive):
        self.__cum_inactive__ = _cum_inactive

    @property
    def s_size(self):
        return self.__s_size__

    @s_size.setter
    def s_size(self, _s_size):
        self.__s_size__ = _s_size

    def __str__(self):
        return ('level: %d, s_size: %d, ' +
               ' frame file: %s, active_start %d, active_stop %d, ' +
               ' inactive_start %d, inactive_stop %d, ' +
               ' inactive_start_2 %d, inactive_stop_2 %d, cum_inactive %d '
               ) \
            % (self.level, self.s_size, self.frame_file,
               self.active_start, self.active_stop,
               self.inactive_start, self.inactive_stop,
               self.inactive_start_2, self.inactive_stop_2, self.cum_inactive
               )


def create_mini_poincare_plot_standard_generation(pp_spec_or_pp_specs_manager):
    movie_maker = PoincarePlotMovieMakerWorker(pp_spec_or_pp_specs_manager)
    if movie_maker.initiate():
        movie_maker.fig.savefig(movie_maker.p0.frame_file,
                                dpi=movie_maker.movie_dpi)
        for idx, p in enumerate(movie_maker.pp_specs[1:]):
            movie_maker.plot(idx)
            movie_maker.fig.savefig(p.frame_file, dpi=movie_maker.movie_dpi)
        plt.close('all')
        gc.collect()  # 'to force' garbage collection


def create_mini_poincare_plot_animated_generation(pp_specs_manager):
    PoincarePlotAnimation(pp_specs_manager)
    plt.close('all')
    gc.collect()  # 'to force' garbage collection


def create_mini_poincare_plot_experimental(pp_specs_manager):
    print('\nWarning !! Experimental code ! Not implemented !\n')


def create_mini_poincare_plot_fast_generation(pp_specs_manager):
    movie_worker = PoincarePlotFastMovieMakerWorker(pp_specs_manager)
    if movie_worker.initiate():
        for idx, _ in enumerate(movie_worker.pp_specs):
            movie_worker.plot(idx)
