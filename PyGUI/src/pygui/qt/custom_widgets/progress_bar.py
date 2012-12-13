'''
Created on 13-12-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.threads import ThreadTask
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import createProgressBar
from pygui.qt.utils.widgets import createPushButton


class ProgressBarManager(object):

    def __init__(self, parent=None, **params):
        self.progressBarComposite = None
        self.threadTask = None
        if parent:
            self.setParams(parent, **params)

    def setParams(self, parent, **params):
        self.parent = parent
        self.params = Params(**params)
        self.progressBarComposite = createComposite(parent,
                                            layout=QHBoxLayout())
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.progressBar = createProgressBar(self.progressBarComposite,
                                             sizePolicy=sizePolicy)
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)
        if self.params.hidden == True:
            self.progressBarComposite.hide()

        self.stopButton = createPushButton(
                                self.progressBarComposite,
                                i18n="datasource.stop.progress.bar.button",
                                i18n_def="Stop")
        self.progressBarComposite.connect(self.stopButton,
                                          SIGNAL("clicked()"),
                                          self.stop)
        self.threadTask = None
        self.local_params = None

    def show(self):
        if self.progressBarComposite:
            self.progressBarComposite.show()

    def hide(self, reset=True):
        if self.progressBarComposite:
            self.progressBarComposite.hide()

    def reset(self):
        if self.progressBarComposite:
            self.progressBar.reset()

    def setValue(self, value):
        if self.progressBarComposite:
            self.progressBar.setValue(0)

    def tick(self):
        self.setValue(0)

    def start(self, **params):
        self.local_params = Params(**params)
        if self.local_params.before:
            self.local_params.before()

        if self.threadTask:
            self.threadTask.stop()
            self.threadTask.setTask(self.local_params.progressJob)
            self.threadTask.setUpdateTask(updateTaskName='taskUpdated',
                                          updateAction=self.tick)
            self.threadTask.setFinishTask(finishTaskName='taskFinished',
                                          finishAction=self.stop)
        else:

            self.threadTask = ThreadTask(self.parent,
                                        updateTaskName='taskUpdated',
                                        updateAction=self.tick,
                                        task=self.local_params.progressJob,
                                        finishTaskName='taskFinished',
                                        finishAction=self.stop)
        if self.threadTask:
            if self.params.hidden == True:
                self.show()
            self.reset()
            if not self.params.progressJob == None:
                self.threadTask.setTask(self.params.progressJob)
            if not self.local_params.progressJob == None:
                self.threadTask.setTask(self.local_params.progressJob)
            self.threadTask.start()

    def stop(self):
        if self.progressBarComposite == None:
            return
        if self.threadTask == None:
            return
        if self.threadTask and self.threadTask.isStopped() == False:
            self.threadTask.stop()
        if not self.local_params == None:
            if not self.local_params.after == None:
                self.local_params.after()
        if self.params.hidden == True:
            self.hide()
        self.reset()

    def close(self):
        self.stop()
        if self.threadTask:
            self.threadTask.close()

    def isStopped(self):
        if self.progressBarComposite == None:
            return False
        if not self.threadTask == None:
            return self.threadTask.isStopped()
        return True

    def update(self):
        if self.threadTask:
            if self.isStopped() == False:
                self.threadTask.emitUpdateTask()
        return not self.isStopped()
