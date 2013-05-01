'''
Created on 24 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections_utils import nvl
    from pymath.time_domain.poincare_plot.poincare_plot_generator import PoincarePlotGenerator # @IgnorePep8
    from pygui.qt.utils.windows import ErrorWindow
    from pygui.qt.custom_widgets.progress_bar import ProgressDialogManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotGeneratorProgressBar(object):
    """
    class represents progress bar shown during calculation of poincare plot
    statistical parameters
    """
    def __init__(self, parent, data_vector_accessor_list, label_text=None,
                max_value=None, **params):
        self.parent = parent
        self.label_text = nvl(label_text, "Poincare plot generation")
        self.max_value = max_value
        self.__data_vector_accessor_list__ = data_vector_accessor_list
        self.params = Params(**params)

    def start(self):
        """
        method initiate show up of poincare progress bar
        """
        self.__interrupted__ = False

        #parameter formatted_summary_statistics is used to store
        #calculated summary statistics
        if not self.params.formatted_summary_statistics == None:
            self.params.formatted_summary_statistics[:] = []

        for data_vector_accessor in self.__data_vector_accessor_list__:
            pp_generator = PoincarePlotGenerator(
                        **data_vector_accessor.parameters_container.parameters)
            message = pp_generator.checkParameters(self.params.check_level)
            if message:
                ErrorWindow(message=message)
                return
            count = pp_generator.segment_count(data_vector_accessor.data_vector) # @IgnorePep8

            #add artificially 1% of the count to avoid the second show
            #of progress bar when in fact total number of segment count
            #is greater then total count calculated by segment_count method
            count = count + int(count * (1 / 100))

            progressManager = ProgressDialogManager(self.parent,
                                            label_text=self.label_text,
                                            max_value=count)
            with progressManager as progress:
                progress_handler = self.__ProgressHandler__()
                progress_handler.progress = progress
                pp_generator.generate(data_vector_accessor.data_vector,
                                      start_progress=None,
                                      progress_handler=progress_handler)
                #store information about interrupt signal if it has happened
                self.__interrupted__ = progress_handler.interrupted

                if self.__interrupted__ == False and \
                    not self.params.formatted_summary_statistics == None:
                    self.params.formatted_summary_statistics.append(
                                  pp_generator.formatted_summary_statistics)

#            for idx in range(count):
#                if (progress.wasCanceled()):
#                    break
#                progress.increaseCounter()

    def interrupted(self, clear=True):
        """
        returns true if progress bar is interrupted
        """
        interrupted = self.__interrupted__
        if clear:
            self.__interrupted__ = False
        return interrupted

    class __ProgressHandler__(object):
        """
        callable class used during processing of poincare plots
        to increase a counter or intercept cancel signal
        """
        def __call__(self):
            self.progress.increaseCounter()

        @property
        def interrupted(self):
            return self.progress.wasCanceled()
