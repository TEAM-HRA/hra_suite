'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_math.model.parameters.core_parameters import CoreParameters
    from hra_math.model.parameters.poincare_plot_parameters \
        import PoincarePlotParameters
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from hra_gui.qt.widgets.number_edit_widget import NumberEditWidget
    from hra_gui.qt.custom_widgets.choose_color_widget import ChooseColorWidget
    from hra_gui.qt.plots.specific_widgets.poincare_plot_movie_generator_progress_bar import PoincarePlotMovieGeneratorProgressBar # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotMovieDockWidget(DockWidgetWidget):
    """
    a dock widget give ability to generate poincare plot movie
    Warning ! there are codecs required: ffmpeg, ffplay, ffprobe
              to generate a movie
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)

        self.data_vectors_accessor_group = \
            self.params.data_vectors_accessor_group  # alias
        if not self.data_vectors_accessor_group == None:
            self.main_data_accessor = \
                self.data_vectors_accessor_group.group_data_vector_accessor
        else:
            self.main_data_accessor = self.params.data_accessor  # alias

        super(PoincarePlotMovieDockWidget, self).__init__(parent,
                title=params.get('title', 'Poincare plot movie maker'),
                **params)

        self.__composite__ = CompositeWidget(self.dockComposite,
                                             layout=QHBoxLayout())

        self.__active_color__ = ChooseColorWidget(self.__composite__,
                                                 title='Active plot color',
                                                 default_color=Qt.red)

        self.__inactive_color__ = ChooseColorWidget(self.__composite__,
                                                 title='Inactive plot color',
                                                 default_color=Qt.black)

        self.__centroid_color__ = ChooseColorWidget(self.__composite__,
                                                 title='Centroid color',
                                                 default_color=Qt.green)

        self.__fps__ = NumberEditWidget(self.__composite__,
                                    #text_changed_handler=self.__min_handler__
                                    )

        PushButtonWidget(self.__composite__,
                            i18n="poincare.plot.movie.generate.button",
                            i18n_def="Generate movie",
                            clicked_handler=self.__generate_handler__)

        parent.addDockWidget(Qt.LeftDockWidgetArea, self)

    def __generate_handler__(self):

        self.main_data_accessor.prepareParametersContainer()
        data_accessors = [self.main_data_accessor]
        #movie_parameters = MovieParameters()
        movie_parameters = PoincarePlotParameters()
        movie_parameters.fps = self.__fps__.getNumber()
        pp_movie_generator_progress_bar = \
            PoincarePlotMovieGeneratorProgressBar(self,
                data_accessors,
                movie_parameters,
                check_level=CoreParameters.LOW_CHECK_LEVEL
                #output_file_listener=self.params.output_file_listener
                # label_text='Statistics calculation',
                #check_level=check_level, save_csv=save_csv,
                #formatted_summary_statistics=formatted_summary_statistics,
                #output_file_listener=self.params.output_file_listener
                )
        pp_movie_generator_progress_bar.start()
