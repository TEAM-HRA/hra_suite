from pymath.utils.utils import print_import_error
try:
    import os
    import pylab as pl
    from pycore.datetime_utils import get_time_label_for_miliseconds
    from pycore.misc import Params
    from pycore.misc import ColorRGB
    from pycore.io_utils import as_path
    from matplotlib.pyplot import savefig
    #matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
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
        self.fig = plt.figure()
        self.__p__ = movie_parameters
        if not self.__p__.movie_name == None:
            self.params = Params(**params)
            self.ax = self.fig.add_subplot(1, 1, 1, adjustable='box',
                                           aspect=1.0)

            if not self.params.filter_manager == None:
                data_vector = self.params.filter_manager.run_filters(
                                                                data_vector)
            _max = pl.amax(data_vector.signal)
            _min = pl.amin(data_vector.signal)

            margin = 50
            self.range = [_min - margin, _max + margin,
                          _min - margin, _max + margin]
            self.ax.axis(self.range)
            self.x_data = None
            self.y_data = None
            self.old_signal_plus = None
            self.empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                                             edgecolor='none', linewidth=0)
            self.idx = 0
            self.__active_color__ = get_color_array(
                                        movie_parameters.movie_active_color)
            self.__inactive_color__ = get_color_array(
                                        movie_parameters.movie_inactive_color)
            self.__centroid_color__ = get_color_array(
                                        movie_parameters.movie_centroid_color)
            self.__info_message__ = None

    def add_data_vector_segment(self, data_vector_segment):
        self.__info_message__ = None
        if self.__p__.movie_name == None:
            return

        frame_file = as_path(self.__p__.movie_dir, '%06d.png' % self.idx)
        skip_frame = True if self.idx < self.__p__.movie_start_frame or \
            (self.__p__.movie_skip_frames and os.path.exists(frame_file)) \
            else False

        if skip_frame == False:
            self.ax = self.fig.add_subplot(1, 1, 1, adjustable='box',
                                           aspect=1.0)
            self.ax.set_xlabel('$RR_{n}$ [ms]')
            self.ax.set_ylabel('$RR_{n+1}$ [ms]')
            self.ax.axis(self.range)

            if self.x_data == None:
                time_label = get_time_label_for_miliseconds(0)
            else:
                time_label = get_time_label_for_miliseconds(pl.sum(self.x_data)) # @IgnorePep8
            leg_time = self.ax.legend([self.empty_rectangle], [time_label],
                                  'upper left')
            leg_time.get_frame().set_alpha(0.5)
            ltext = leg_time.get_texts()
            plt.setp(ltext, fontsize=8)
            self.ax.add_artist(leg_time)

            mean_plus = pl.mean(data_vector_segment.signal_plus)
            mean_minus = pl.mean(data_vector_segment.signal_minus)

        if self.x_data == None:
            self.x_data = data_vector_segment.signal_plus.copy()
            self.y_data = data_vector_segment.signal_minus.copy()

            if skip_frame == False:
                a_plot = self.ax.scatter(self.x_data, self.y_data,
                                         c=self.__active_color__,
                                         s=self.__p__.movie_active_size)
                c_plot = self.ax.scatter([mean_plus], [mean_minus],
                                         c=self.__centroid_color__,
                                         s=self.__p__.movie_centroid_size)

                if self.__p__.show_plot_legends == True:
                    leg_plots = self.ax.legend((a_plot, c_plot),
                                               ('biezacy PP', "controid"),
                                               'upper right', scatterpoints=1)
                    leg_plots.get_frame().set_alpha(0.5)
            ok = True
        else:
            s_plus = len(data_vector_segment.signal_plus)
            old_s_plus = len(self.old_signal_plus)
            ok = False
            if s_plus >= old_s_plus:
                for idx in xrange(1, old_s_plus):
                    if pl.all(self.old_signal_plus[idx:] \
                                == data_vector_segment.signal_plus[idx - 1:
                                                            old_s_plus - idx]):
                        self.x_data = pl.hstack((self.x_data,
                            data_vector_segment.signal_plus[old_s_plus -
                                                             idx:]))
                        self.y_data = pl.hstack((self.y_data,
                            data_vector_segment.signal_minus[old_s_plus -
                                                              idx:]))
                        if skip_frame == False:
                            inactive_idx = len(self.x_data) - s_plus
                            i_plot = self.ax.scatter(
                                            self.x_data[:inactive_idx],
                                            self.y_data[:inactive_idx],
                                            c=self.__inactive_color__,
                                            s=self.__p__.movie_inactive_size)
                            a_plot = self.ax.scatter(
                                            self.x_data[inactive_idx:],
                                            self.y_data[inactive_idx:],
                                            c=self.__active_color__,
                                            s=self.__p__.movie_active_size)
                            c_plot = self.ax.scatter([mean_plus], [mean_minus],
                                            c=self.__centroid_color__,
                                            s=self.__p__.movie_centroid_size)
                        ok = True
                        break
            else:
                for idx in xrange(1, old_s_plus):
                    if idx + s_plus <= old_s_plus \
                        and pl.all(self.old_signal_plus[idx:idx + s_plus] \
                                    == data_vector_segment.signal_plus):
                        if skip_frame == False:
                            inactive_idx = len(self.x_data) - old_s_plus + idx
                            self.ax.scatter(self.x_data[:inactive_idx],
                                        self.y_data[:inactive_idx],
                                        c=self.__inactive_color__,
                                        s=self.__p__.movie_inactive_size)
                            i_plot = self.ax.scatter(
                                        self.x_data[inactive_idx + s_plus:],
                                        self.y_data[inactive_idx + s_plus:],
                                        c=self.__inactive_color__,
                                        s=self.__p__.movie_inactive_size)
                            a_plot = self.ax.scatter(
                                        self.x_data[inactive_idx:
                                                    inactive_idx + s_plus],
                                        self.y_data[inactive_idx:
                                                    inactive_idx + s_plus],
                                        c=self.__active_color__,
                                        s=self.__p__.movie_active_size)
                            c_plot = self.ax.scatter([mean_plus], [mean_minus],
                                        c=self.__centroid_color__,
                                        s=self.__p__.movie_centroid_size)
                        ok = True
                        #_save = False
                        break

        if skip_frame == False and self.__p__.show_plot_legends == True:
            leg_plots = self.ax.legend((a_plot, i_plot, c_plot),
                   ('biezacy PP', "poprzednie PP", "controid"),
                   'upper right', scatterpoints=1)  # , shadow=True)
            leg_plots.get_frame().set_alpha(0.5)
            ltext = leg_plots.get_texts()
            plt.setp(ltext, fontsize=8)

        if ok == True:
            if skip_frame:
                self.__info_message__ = 'File %s skipped' % (frame_file)
            else:
                savefig(frame_file, dpi=self.__p__.movie_dpi)
                if self.params.segment_count == None:
                    self.__info_message__ = 'Wrote file: %s' % (frame_file)
                else:
                    self.__info_message__ = 'Wrote file: %s [%07d/%07d]' % \
                            (frame_file, self.idx, self.params.segment_count)

        self.old_signal_plus = data_vector_segment.signal_plus
        self.idx = self.idx + 1
        if skip_frame == False:
            plt.cla()

    def save_movie(self):
        if not self.__p__.movie_name == None:
            output_movie_file = as_path(self.__p__.movie_dir,
                                        '%s.avi' % (self.__p__.movie_name))
            command = ('mencoder',
                       'mf://' + self.__p__.movie_dir + '/*.png',
                       '-mf',
                       #'type=png:w=1024:h=800:fps=30',
                       'type=png:w=' + str(self.__p__.movie_width) + \
                            ':h=' + str(self.__p__.movie_height) + \
                            ':fps=' + str(self.__p__.movie_fps),
                       '-ovc',
                       'lavc',
                       '-lavcopts',
                       'vcodec=mpeg4',
                       '-oac',
                       'copy',
                       '-o',
                       '%s' % (output_movie_file))
            os.spawnvp(os.P_WAIT, 'mencoder', command)
            self.__info_message__ = \
                "Poincare plot movie %s is created !" % (output_movie_file)

    @property
    def info_message(self):
        return self.__info_message__
