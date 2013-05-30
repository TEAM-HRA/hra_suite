'''
Created on 13-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.widgets.progress_dialog_widget import ProgressDialogWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ProgressDialogManager(object):
    def __init__(self, parent, **params):
        self.parent = parent
        self.params = params

        #if present means how many times a progress dialog will be called
        self.__count__ = params.get('count', None)
        self.__idx__ = self.__count__

    def initialize(self, **params):
        """
        this method could be used in context managers,
        the scenario is the following:
        progressManager = ProgressDialogManager(..., count=value)
        for something in iterator:
            with progressManager.initialize(...) as progress:
        """
        if self.params:  # update existing params
            self.params.update(params)
        else:
            self.params = params
        #this method have to return self object in order to be used
        #in context manager
        return self

    def __enter__(self):

        if self.__count__:  # add counter indicator
            label_text = self.params.get('label_text', '')
            self.params['label_text'] = "[{0}/{1}] {2}".format(
                        self.__idx__, self.__count__, label_text)
            self.__idx__ -= 1

        self.progress_bar = ProgressDialogWidget(self.parent, **self.params)
        self.progress_bar.setWindowModality(Qt.WindowModal)
        self.progress_bar.setMinimumDuration(0)
        self.progress_bar.forceShow()
        return self.progress_bar

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.progress_bar.close()

#  ******************************************************************
#   don't remove the following code, stayed for educational purposes
#  ******************************************************************
#
#PROGRESS_ITERATOR_SIGNAL = SIGNAL('progress_iterator_item(PyQt_PyObject)')
#
#signal emitted when progress bar emits finish signal
#PROGRESS_FINISH_SIGNAL = SIGNAL('finish()')
#class AbstractProgressIterator(QObject):
#    """
#    this class have to be implemented in a client's code
#    """
#    def __init__(self, parent=None):
#        super(AbstractProgressIterator, self).__init__(parent)
#
#    def hasNext(self):
#        return False
#
#    def next(self):
#        pass
#
#    def getIterator(self):
#        pass
#
#
#class ProgressJob(QObject):
#    def __init__(self, progressIterator, size=0, parent=None):
#        super(ProgressJob, self).__init__(parent)
#        self.progressIterator = progressIterator
#        self.finished = False
#        self.__size__ = size
#
#    @pyqtSlot()
#    def started(self):
#        self.finished = False
#        self.progressIterator.getIterator()
#        while(self.progressIterator.hasNext()):
#            if self.finished:
#                break
#            self.emit(PROGRESS_ITERATOR_SIGNAL,
#                      self.progressIterator.next())
#            # improves GUI responsiveness
#            QThread.currentThread().usleep(1)
#        self.emit(PROGRESS_FINISH_SIGNAL)
#
#    @pyqtSlot()
#    def finish(self):
#        self.finished = True
#
#    def size(self):
#        return self.__size__
#
##    def getProgressIterator(self):
##        return self.__progressIterator__
#
#
#class ProgressBarManager(QObject):
#
#    def __init__(self, parent=None, **params):
#        super(ProgressBarManager, self).__init__(parent)
#        self.parent = parent
#        self.params = Params(**params)
#        self.local_params = None
#        self.size = 0
#        self.counter = 0
#        self.stopped = False
#
#        self.progressBarComposite = CompositeWidget(parent,
#                                layout=QHBoxLayout(),
#                                hide_event_handler=self.__hideEventHandler__)
#        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
#        self.progressBar = ProgressBarWidget(self.progressBarComposite,
#                                             sizePolicy=sizePolicy)
#        if self.params.hidden:
#            self.progressBarComposite.hide()
#        self.progressBar.setRange(0, self.size)
#        self.progressBar.setValue(0)
#
#        self.stopButton = PushButtonWidget(
#                                self.progressBarComposite,
#                                i18n="datasource.stop.progress.bar.button",
#                                i18n_def="Stop",
#                                clicked_handler=self.stoppedByButton
#                                )
#
#    def stoppedByButton(self):
#        self.stopped = True
#        #self.stopButton.emit(PROGRESS_FINISH_SIGNAL)
#        #self.blockSignals(True)
#        self.__stop__()
#
#    @pyqtSlot()
#    def finish(self):
#        self.__stop__()
#
#    def __stop__(self):
#        self.progressBarComposite.hide()
#        if self.local_params and self.local_params.after:
#            self.local_params.after()
#
#    def __progressBarHandler__(self, _object):
#        if self.progress_handler:
#            self.progress_handler(_object)
#            if self.size > 0:
#                self.counter = self.counter + 1
#                self.progressBar.setValue(self.counter)
#
#    def start(self, progress_job=None, progress_handler=None, **params):
#        self.blockSignals(False)
#        self.stopped = False
#        self.local_params = Params(**params)
#        if not progress_handler or not progress_job:
#            return
#        if self.params.hidden:
#            self.progressBarComposite.show()
#
#        self.progress_job = progress_job
#        self.progress_handler = progress_handler
#
#        self.counter = 0
#        if self.local_params.size > 0 or self.progress_job.size() > 0:
#            self.size = nvl(self.local_params.size, self.progress_job.size(), 0) # @IgnorePep8
#        else:
#            self.size = 0
#        self.progressBar.reset()
#        self.progressBar.setRange(0, self.size)
#        self.progressBar.setValue(0)
#
#        self.thread = QThread()
#        self.progress_job.moveToThread(self.thread)
#
#        #self.connect(thread, SIGNAL('started()'), reader, reader.started)
#        self.connect(self.thread, SIGNAL('started()'), self.progress_job, SLOT('started()')) # @IgnorePep8
#        #self.connect(reader, SIGNAL('file_found(PyQt_PyObject)'), self, self.file_found) # @IgnorePep8
#        self.connect(self.progress_job, PROGRESS_ITERATOR_SIGNAL, self.__progressBarHandler__) # @IgnorePep8
#        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.thread, SLOT('quit()')) # @IgnorePep8
#        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self, SLOT('finish()')) # @IgnorePep8
#        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.progress_job, SLOT('finish()')) # @IgnorePep8
#        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.progress_job, SLOT('deleteLater()')) # @IgnorePep8
#
#        #for stop button
#        self.connect(self.stopButton, PROGRESS_FINISH_SIGNAL, self.thread, SLOT('quit()')) # @IgnorePep8
#        self.connect(self.stopButton, PROGRESS_FINISH_SIGNAL, self, SLOT('finish()')) # @IgnorePep8
#        #self.connect(self.stopButton, PROGRESS_FINISH_SIGNAL, self.progress_job, SLOT('deleteLater()')) # @IgnorePep8
#
##        self.connect(self.parent, SIGNAL('close()'), self.thread, SLOT('quit()')) # @IgnorePep8
##        self.connect(self.parent, SIGNAL('close()'), self.progress_job, SLOT('finish()')) # @IgnorePep8
##        self.connect(self.parent, SIGNAL('deleteLater()'), self.thread, SLOT('quit()')) # @IgnorePep8
##        self.connect(self.parent, SIGNAL('deleteLater()'), self.progress_job, SLOT('finish()')) # @IgnorePep8        
#
#        #self.connect(reader, SIGNAL('finished()'), thread, SLOT('deleteLater()')) # @IgnorePep8
#        #J.E self.connect(reader, SIGNAL('finished()'), thread, SLOT('quit()')) # @IgnorePep8
#        #delete thread only when thread has really finished
#        self.connect(self.thread, PROGRESS_FINISH_SIGNAL, self.thread, SLOT('deleteLater()')) # @IgnorePep8
#        self.connect(self.thread, SIGNAL('terminated()'), self.thread, SLOT('deleteLater()')) # @IgnorePep8
#
#        if self.local_params.before:
#            self.local_params.before()
#        self.thread.start()
#
#    def __hideEventHandler__(self, event):
#        if not self.progressBarComposite.isVisible():
#            if hasattr(self, 'progress_job'):
#                self.progress_job.finish()
#
#    def isStopped(self):
#        return self.stopped
#
#
#class CounterProgressIterator(AbstractProgressIterator):
#    """
#    this is a simple iterator runs over range of numbers
#    """
#    def __init__(self, size, start=0):
#        super(CounterProgressIterator, self).__init__(None)
#        self.__size__ = size
#        self.idx = start
#
#    def getIterator(self):
#        return range(self.__size__)
#
#    def hasNext(self):
#        return self.idx < self.size
#
#    def next(self):
#        idx = self.idx
#        self.idx = self.idx + 1
#        return idx
#
#    @property
#    def size(self):
#        return self.__size__
#
#
#class CounterProgressJob(ProgressJob):
#    def __init__(self, size, parent=None):
#        super(CounterProgressJob, self).__init__(
#                   CounterProgressIterator(size), size=size, parent=parent)
#
#    def start(self, progress_job=None, progress_handler=None, **params):
#        super(CounterProgressJob, self).start(progress_job, progress_handler,
#                                              **params)
#
