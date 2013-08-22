'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import multiprocessing
    import pylab as pl
    from pycore.misc import ColorRGB
    from pycore.collections_utils import nvl
    from pymath.model.core_parameters import CoreParameters
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotMovieParameters(CoreParameters):
    """
    specific parameters concerning poincare plot movie
    """

    NAME = "poincare_plot_movie_parameters"

    @property
    def movie_name(self):
        """
        [required to allow movie functionality]
        a movie name, if present the movie will be created
        """
        return self.__movie_name__

    @movie_name.setter
    def movie_name(self, _movie_name):
        self.__movie_name__ = _movie_name

    @property
    def movie_fps(self):
        """
        [optional]
        get movie_fps of a movie [default: 700]
        """
        return nvl(self.__movie_fps__, 700)

    @movie_fps.setter
    def movie_fps(self, _movie_fps):
        self.__movie_fps__ = _movie_fps

    @property
    def movie_active_color(self):
        """
        [optional]
        color of active poincare plot [default: red]
        """
        return nvl(self.__movie_active_color__, ColorRGB(255, 0, 0))

    @movie_active_color.setter
    def movie_active_color(self, _movie_active_color):
        self.__movie_active_color__ = _movie_active_color

    @property
    def movie_inactive_color(self):
        """
        [optional]
        color of inactive poincare plot [default: black]
        """
        return nvl(self.__movie_inactive_color__, ColorRGB(0, 0, 0))

    @movie_inactive_color.setter
    def movie_inactive_color(self, _movie_inactive_color):
        self.__movie_inactive_color__ = _movie_inactive_color

    @property
    def movie_centroid_color(self):
        """
        [optional]
        color of a centroid [default: green]
        """
        _color = pl.array([255, 0, 0]) / 255
        return nvl(self.__movie_centroid_color__, ColorRGB(0, 255, 0))

    @movie_centroid_color.setter
    def movie_centroid_color(self, _movie_centroid_color):
        self.__movie_centroid_color__ = _movie_centroid_color

    @property
    def movie_active_size(self):
        """
        [optional]
        size of an active plot point [default: 20 [points]]
        """
        return nvl(self.__movie_active_size__, 20)

    @movie_active_size.setter
    def movie_active_size(self, _movie_active_size):
        self.__movie_acitive_size__ = _movie_active_size

    @property
    def movie_inactive_size(self):
        """
        [optional]
        size of a inactive plot point [default: 10 [points]]
        """
        return nvl(self.__movie_inactive_size__, 10)

    @movie_inactive_size.setter
    def movie_inactive_size(self, _inactive_size):
        self.__inacitive_size__ = _inactive_size

    @property
    def movie_centroid_size(self):
        """
        [optional]
        size of a point's centroid [default: 40 [points]]
        """
        return nvl(self.__movie_centroid_size__, 40)

    @movie_centroid_size.setter
    def movie_centroid_size(self, _movie_centroid_size):
        self.__movie_centroid_size__ = _movie_centroid_size

    @property
    def movie_dpi(self):
        """
        [optional]
        movie DPI resolution [default: 100]
        """
        return nvl(self.__movie_dpi__, 100)

    @movie_dpi.setter
    def movie_dpi(self, _movie_dpi):
        self.__movie_dpi__ = _movie_dpi

    @property
    def movie_height(self):
        """
        [optional]
        movie height [default: 800]
        """
        return nvl(self.__movie_height__, 800)

    @movie_height.setter
    def movie_height(self, _movie_height):
        self.__movie_height__ = _movie_height

    @property
    def movie_width(self):
        """
        [optional]
        movie width [default: 800]
        """
        return nvl(self.__movie_width__, 800)

    @movie_width.setter
    def movie_width(self, _movie_width):
        self.__movie_width__ = _movie_width

    @property
    def movie_dir(self):
        """
        [optional]
        directory where a movie will be put
        """
        return nvl(self.__movie_dir__, '')

    @movie_dir.setter
    def movie_dir(self, _movie_dir):
        self.__movie_dir__ = _movie_dir

    @property
    def movie_skip_frames(self):
        """
        [optional]
        skip existing frames [default: True]
        """
        return nvl(self.__movie_skip_frames__, True)

    @movie_skip_frames.setter
    def movie_skip_frames(self, _movie_skip_frames):
        self.__movie_skip_frames__ = _movie_skip_frames

    @property
    def movie_save_partial(self):
        """
        [optional]
        save partial movie [default: True]
        """
        return nvl(self.__movie_save_partial__, True)

    @movie_save_partial.setter
    def movie_save_partial(self, _movie_save_partial):
        self.__movie_save_partial__ = _movie_save_partial

    @property
    def movie_skip_to_frame(self):
        """
        [optional]
        skip to a movie frame [default: 0]
        """
        return nvl(self.__movie_skip_to_frame__, 0)

    @movie_skip_to_frame.setter
    def movie_skip_to_frame(self, _movie_skip_to_frame):
        self.__movie_skip_to_frame__ = _movie_skip_to_frame

    @property
    def movie_not_save(self):
        """
        [optional - default: False]
        not save frames, not save a movie, only for testing purposes
        """
        return nvl(self.__movie_not_save__, False)

    @movie_not_save.setter
    def movie_not_save(self, _movie_not_save):
        self.__movie_not_save__ = _movie_not_save

    @property
    def movie_show_plot_legends(self):
        """
        [optional - default: False]
        show plot legends
        """
        return nvl(self.__movie_show_plot_legends__, False)

    @movie_show_plot_legends.setter
    def movie_show_plot_legends(self, _movie_show_plot_legends):
        self.__movie_show_plot_legends__ = _movie_show_plot_legends

    @property
    def movie_multiprocessing_factor(self):
        """
        [optional - default: 3]
        multiprocessing factor if multiprocessing is available
        if this is not the case value equals 0
        """
        return nvl(self.__movie_multiprocessing_factor__,
                                3 if multiprocessing.cpu_count() > 1 else 0)

    @movie_multiprocessing_factor.setter
    def movie_multiprocessing_factor(self, _movie_multiprocessing_factor):
        self.__movie_multiprocessing_factor__ = _movie_multiprocessing_factor

    @property
    def movie_bin_size(self):
        """
        [optional - default: False]
        movie bin size; for internal use [default: 500]
        """
        return nvl(self.__movie_bin_size__, 500)

    @movie_bin_size.setter
    def movie_bin_size(self, _movie_bin_size):
        self.__movie_bin_size__ = _movie_bin_size

    @property
    def movie_experimental_code(self):
        """
        [optional]
        use some experimental code; only for tests [default: False]
        """
        return nvl(self.__movie_experimental_code__, False)

    @movie_experimental_code.setter
    def movie_experimental_code(self, _movie_experimental_code):
        self.__movie_experimental_code__ = _movie_experimental_code

    @property
    def movie_animated(self):
        """
        [optional - default: False]
        use of animation API to generate a movie
        """
        return nvl(self.__movie_animated__, False)

    @movie_animated.setter
    def movie_animated(self, _movie_animated):
        self.__movie_animated__ = _movie_animated

    def setObjectPoincarePlotMovieParameters(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'movie_name', self.movie_name)
        setattr(_object, 'movie_fps', self.movie_fps)
        setattr(_object, 'movie_active_color', self.movie_active_color)
        setattr(_object, 'movie_inactive_color', self.movie_inactive_color)
        setattr(_object, 'movie_centroid_color', self.movie_centroid_color)
        setattr(_object, 'movie_active_size', self.movie_active_size)
        setattr(_object, 'movie_inactive_size', self.movie_inactive_size)
        setattr(_object, 'movie_centroid_size', self.movie_centroid_size)
        setattr(_object, 'movie_dpi', self.movie_dpi)
        setattr(_object, 'movie_dir', self.movie_dir)
        setattr(_object, 'movie_skip_frames', self.movie_skip_frames)
        setattr(_object, 'movie_height', self.movie_height)
        setattr(_object, 'movie_width', self.movie_width)
        setattr(_object, 'movie_save_partial', self.movie_save_partial)
        setattr(_object, 'movie_skip_to_frame', self.movie_skip_to_frame)
        setattr(_object, 'movie_not_save', self.movie_not_save)
        setattr(_object, 'movie_show_plot_legends',
                            self.movie_show_plot_legends)
        setattr(_object, 'movie_multiprocessing_factor',
                            self.movie_multiprocessing_factor)
        setattr(_object, 'movie_bin_size', self.movie_bin_size)
        setattr(_object, 'movie_animated', self.movie_animated)
        setattr(_object, 'movie_experimental_code',
                            self.movie_experimental_code)

    def validatePoincarePlotMovieParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        if self.movie_name == None:
            return "Name of a movie is required"
        if self.movie_dir == None:
            return "Movie directory is required"

    def parameters_infoPoincarePlotMovieParameters(self):
        if not self.movie_name == None:
            print('Movie specifiaction: ')
            print('    name: ' + str(self.movie_name))
            print('    directory: ' + str(self.movie_dir))
            print('    height: ' + str(self.movie_height))
            print('    width: ' + str(self.movie_width))
            print('    FPS: ' + str(self.movie_fps))
            print('    active plot color: ' + str(self.movie_active_color))
            print('    inactive plot color: ' +
                                        str(self.movie_inactive_color))
            print('    centroid color: ' + str(self.movie_centroid_color))
            print("    active plot point's size: " +
                                                str(self.movie_active_size))
            print("    inactive plot point's size: " +
                                            str(self.movie_inactive_size))
            print("    centroid point's size: " +
                                            str(self.movie_centroid_size))
            print('    DPI: ' + str(self.movie_dpi))
            print('    skip existing frames: ' + str(self.movie_skip_frames))
            print('    save partial movie: ' + str(self.movie_save_partial))
            print('    skip to frame: ' + str(self.movie_skip_to_frame))
            print('    show plot legends: ' +
                                        str(self.movie_show_plot_legends))
            print('    movie multiprocessing factor: ' +
                                        str(self.movie_multiprocessing_factor))
            print('    movie bin size: ' + str(self.movie_bin_size))
            print('    use animation API: ' + str(self.movie_animated))
            print('    use experimental code: '
                                         + str(self.movie_experimental_code))
