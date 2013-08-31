'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_core.collections_utils import nvl
    from hra_math.time_domain.poincare_plot.poincare_plot_generator import PoincarePlotGenerator # @IgnorePep8
    from hra_math.time_domain.poincare_plot.poincare_plot_generator import ProgressHandlerGenerator # @IgnorePep8
    from hra_math.time_domain.poincare_plot.poincare_plot_generator import StartProgressGenerator # @IgnorePep8
    from hra_gui.qt.utils.windows import ErrorWindow
    from hra_gui.qt.utils.windows import InformationWindow
    from hra_gui.qt.custom_widgets.progress_bar import ProgressDialogManager
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

        outcomes_exist_info = []
        progressManager = ProgressDialogManager(self.parent,
                                count=len(self.__data_vector_accessor_list__))
        for data_vector_accessor in self.__data_vector_accessor_list__:
            pp_generator = PoincarePlotGenerator(
                        output_file_listener=self.params.output_file_listener,
                        **data_vector_accessor.parameters_container.parameters)
            if self.params.save_csv == True:
                (ok, _) = pp_generator.precheck(
                                        data_vector_accessor.source_name)
                if ok == False:
                    if pp_generator.outcome_exists:
                        outcomes_exist_info.append(
                                        data_vector_accessor.source_name)
                    continue

            message = pp_generator.checkParameters(self.params.check_level)
            if message:
                ErrorWindow(message=message)
                return
            count = pp_generator.segment_count(data_vector_accessor.data_vector) # @IgnorePep8

            #add artificially 1% of the count to avoid the second show
            #of progress bar when in fact total number of segment count
            #is greater then total count calculated by segment_count method
            count = count + int(count * (1 / 100))

            #extends label text with source name (if not None)
            label_text = "{0} [{1}]".format(self.label_text,
                                    nvl(data_vector_accessor.source_name, ""))
            with progressManager.initialize(label_text=label_text,
                                            max_value=count) as progress:
                start_progress = self.__StartProgress__()
                if not self.params.progress_handler == None:
                    #give ability to pass custom progress handler
                    progress_handler = self.params.progress_handler
                elif self.params.save_csv == True:
                    progress_handler = self.__CSVProgressHandler__()
                else:
                    progress_handler = self.__ProgressHandler__()
                progress_handler.progress = progress
                if self.params.save_csv == True:
                    pp_generator.generate_CSV(data_vector_accessor.data_vector,
                                            data_vector_accessor.source_name,
                                            start_progress=start_progress,
                                            progress_handler=progress_handler)
                else:
                    pp_generator.generate(data_vector_accessor.data_vector,
                                          start_progress=start_progress,
                                          progress_handler=progress_handler)
                #store information about interrupt signal if it has happened
                self.__interrupted__ = progress_handler.interrupted

                if self.__interrupted__ == False and \
                    not self.params.formatted_summary_statistics == None:
                    self.params.formatted_summary_statistics.append(
                                  pp_generator.formatted_summary_statistics)

                #if interrupted break the whole loop
                if self.__interrupted__:
                    return
        if len(outcomes_exist_info) > 0:
            message = "For the following files, outcomes already exist:"
            for outcome in outcomes_exist_info:
                message += ("\n" + outcome)
            InformationWindow(message=message)

    def interrupted(self, clear=True):
        """
        returns true if progress bar is interrupted
        """
        interrupted = self.__interrupted__
        if clear:
            self.__interrupted__ = False
        return interrupted

    class __StartProgress__(StartProgressGenerator):
        def __call__(self):
            #ProgressDialogManager fulfills this role
            pass

    class __ProgressHandler__(ProgressHandlerGenerator):
        """
        callable class used during processing of poincare plots
        to increase a counter or intercept cancel signal
        """
        def __call__(self):
            self.progress.increaseCounter()

        @property
        def interrupted(self):
            return self.progress.wasCanceled()

    class __CSVProgressHandler__(__ProgressHandler__):
        """
        callable class used during processing of poincare plots
        to increase a counter or intercept cancel signal
        """
        def __call__(self):
            self.progress.increaseCounter()
            self.csv.write(self.parameters,
                       ordinal_value=self.segmenter.ordinal_value)
