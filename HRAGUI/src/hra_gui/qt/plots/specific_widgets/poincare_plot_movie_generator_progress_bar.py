'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import pylab as pl
    #import matplotlib
    #matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as manimation
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.collections_utils import nvl
    from hra_math.time_domain.poincare_plot.poincare_plot_generator import ProgressHandlerGenerator # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.poincare_plot_generator_progress_bar import PoincarePlotGeneratorProgressBar # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotMovieGeneratorProgressBar(PoincarePlotGeneratorProgressBar):
    """
    class represents progress bar shown during generation of
    movie of a poincare plot
    """
    def __init__(self, parent, data_vector_accessor_list, movie_parameters,
                label_text=None, max_value=None, **params):
        PoincarePlotGeneratorProgressBar.__init__(self,
                parent, data_vector_accessor_list,
                label_text=nvl(label_text, "Poincare plot movie generator"),
                max_value=max_value, **params)
        self.movie_parameters = movie_parameters
        self.data_vector_accessor_list = data_vector_accessor_list

    def start(self):
        self.params.save_csv = False
        with self.__initiate_movie__():
            self.params.progress_handler = __MovieProgressHandler__(
                                                self.writer, self.movie_plot)
            super(PoincarePlotMovieGeneratorProgressBar, self).start()

    def __initiate_movie__(self):
        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Poincare plot movie', artist='HRV',
                        comment='Movie support!')
        self.writer = FFMpegWriter(fps=self.movie_parameters.fps,
                              metadata=metadata)

        self.fig = plt.figure()
        #l, = plt.plot([], [], 'k-o')
        self.movie_plot, = plt.plot([], [], 'bo')

        margin = 50
        signal = self.data_vector_accessor_list[0].signal
        _max = pl.amax(signal)
        _min = pl.amin(signal)
        plt.xlim(_min - margin, _max + margin)
        plt.ylim(_min - margin, _max + margin)
        movie_filename = '/tmp/movie.mp4'
        return self.writer.saving(self.fig, movie_filename, 150)


class __MovieProgressHandler__(ProgressHandlerGenerator):
    def __init__(self, writer, movie_plot):
        self.writer = writer
        self.movie_plot = movie_plot

    """
    callable class used during processing of poincare plots
    to increase a counter or intercept cancel signal
    """
    def __call__(self):
        self.progress.increaseCounter()
        data_vector = self.segmenter.data_vector_segment
        self.movie_plot.set_data(data_vector.signal_plus,
                                 data_vector.signal_minus)
        self.writer.grab_frame()

    @property
    def interrupted(self):
        return self.progress.wasCanceled()
