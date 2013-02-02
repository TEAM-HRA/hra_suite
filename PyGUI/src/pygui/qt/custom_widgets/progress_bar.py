'''
Created on 13-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.signals import PROGRESS_ITERATOR_SIGNAL
    from pygui.qt.utils.signals import PROGRESS_FINISH_SIGNAL
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import ProgressBarCommon
    from pygui.qt.utils.widgets import PushButtonCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class AbstractProgressIterator(QObject):
    """
    this class have to be implemented in a client's code
    """
    def __init__(self, parent=None):
        super(AbstractProgressIterator, self).__init__(parent)

    def hasNext(self):
        return False

    def next(self):
        pass

    def getIterator(self):
        pass


class ProgressJob(QObject):
    def __init__(self, progressIterator, parent=None):
        super(ProgressJob, self).__init__(parent)
        self.progressIterator = progressIterator
        self.finished = False

    @pyqtSlot()
    def started(self):
        self.finished = False
        self.progressIterator.getIterator()
        counter = 0
        while(self.progressIterator.hasNext()):
            self.emit(PROGRESS_ITERATOR_SIGNAL, self.progressIterator.next())
            # improves GUI responsiveness
            if counter % 5 == 0:
                QThread.currentThread().usleep(1)
            counter = counter + 1
            if self.finished:
                break
        self.emit(PROGRESS_FINISH_SIGNAL)

    @pyqtSlot()
    def finish(self):
        self.finished = True


class ProgressBarManager(QObject):

    def __init__(self, parent=None, **params):
        super(ProgressBarManager, self).__init__(parent)
        self.parent = parent
        self.params = Params(**params)
        self.local_params = None

        self.progressBarComposite = CompositeCommon(parent,
                            layout=QHBoxLayout(),
                            hide_event_handler=self.__hideEventHandler__)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.progressBar = ProgressBarCommon(self.progressBarComposite,
                                             sizePolicy=sizePolicy)
        if self.params.hidden:
            self.progressBarComposite.hide()
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)

        self.stopButton = PushButtonCommon(
                                self.progressBarComposite,
                                i18n="datasource.stop.progress.bar.button",
                                i18n_def="Stop")
        self.progressBarComposite.connect(self.stopButton,
                                          SIGNAL("clicked()"),
                                          self.finish)

    @pyqtSlot()
    def finish(self):
        self.progressBarComposite.hide()
        if self.local_params and self.local_params.after:
            self.local_params.after()

    def __progressBarHandler__(self, _object):
        if self.progress_handler:
            self.progress_handler(_object)
        #self.progressBar.setValue(0)

    def start(self, progress_job=None, progress_handler=None, **params):
        self.local_params = Params(**params)
        if not progress_handler or not progress_job:
            return
        if self.params.hidden:
            self.progressBarComposite.show()
        self.progress_job = progress_job
        self.progress_handler = progress_handler
        self.thread = QThread()
        self.progress_job.moveToThread(self.thread)

        #self.connect(thread, SIGNAL('started()'), reader, reader.started)
        self.connect(self.thread, SIGNAL('started()'), self.progress_job, SLOT('started()')) # @IgnorePep8
        #self.connect(reader, SIGNAL('file_found(PyQt_PyObject)'), self, self.file_found) # @IgnorePep8
        self.connect(self.progress_job, PROGRESS_ITERATOR_SIGNAL, self.__progressBarHandler__) # @IgnorePep8
        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.thread, SLOT('quit()')) # @IgnorePep8
        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self, SLOT('finish()')) # @IgnorePep8
        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.progress_job, SLOT('finish()')) # @IgnorePep8
        self.connect(self.progress_job, PROGRESS_FINISH_SIGNAL, self.progress_job, SLOT('deleteLater()')) # @IgnorePep8

#        self.connect(self.parent, SIGNAL('close()'), self.thread, SLOT('quit()')) # @IgnorePep8
#        self.connect(self.parent, SIGNAL('close()'), self.progress_job, SLOT('finish()')) # @IgnorePep8
#        self.connect(self.parent, SIGNAL('deleteLater()'), self.thread, SLOT('quit()')) # @IgnorePep8
#        self.connect(self.parent, SIGNAL('deleteLater()'), self.progress_job, SLOT('finish()')) # @IgnorePep8        

        #self.connect(reader, SIGNAL('finished()'), thread, SLOT('deleteLater()')) # @IgnorePep8
        #J.E self.connect(reader, SIGNAL('finished()'), thread, SLOT('quit()'))
        #delete thread only when thread has really finished
        self.connect(self.thread, PROGRESS_FINISH_SIGNAL, self.thread, SLOT('deleteLater()')) # @IgnorePep8
        self.connect(self.thread, SIGNAL('terminated()'), self.thread, SLOT('deleteLater()')) # @IgnorePep8

        if self.local_params.before:
            self.local_params.before()
        self.thread.start()

    def __hideEventHandler__(self, event):
        if not self.progressBarComposite.isVisible():
            if hasattr(self, 'progress_job'):
                self.progress_job.finish()


class CounterProgressIterator(AbstractProgressIterator):
    """
    this is a simple iterator runs over range of numbers
    """
    def __init__(self, size=0, start=0):
        super(CounterProgressIterator, self).__init__(None)
        self.size = size
        self.idx = start

    def getIterator(self):
        return range(self.size)

    def hasNext(self):
        return self.idx < self.size

    def next(self):
        idx = self.idx
        self.idx = self.idx + 1
        return idx


class CounterProgressJob(ProgressJob):
    def __init__(self, size, parent=None):
        super(CounterProgressJob, self).__init__(CounterProgressIterator(size),
                                                 parent)
