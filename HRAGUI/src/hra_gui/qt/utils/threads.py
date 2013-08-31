'''
Created on 03-12-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ThreadTask(QThread):
    """
    helper class for threads, have to be subclassed
    """
    def __init__(self, parent, **params):
        QThread.__init__(self, parent)
        self.params = Params(**params)

        # loop is stopped and finishAction is executed
        self.__stop__ = False

        # loop is stopped and finishAction is NOT executed
        self.__close__ = False

        # connected the thread with corresponding signal and action
        # for 3 stages: at the start, during loop,
        # at the end (after loop is ended or breaked)
        if not self.params.startAction == None:
            self.connect(self, SIGNAL(self.params.startTaskName),
                         self.params.startAction)
        if not self.params.updateAction == None:
            self.connect(self, SIGNAL(self.params.updateTaskName),
                         self.params.updateAction)
        if not self.params.finishAction == None:
            self.connect(self, SIGNAL(self.params.finishTaskName),
                         self.params.finishAction)
        self.task = self.params.task

    def run(self):
        #counts how many emit update tasks are invoked
        self.__emit_update_counter__ = 0

        self.__stop__ = False
        self.__close__ = False

        #emit signal before main loop
        if self.params.startTaskName:
            self.emit(SIGNAL(self.params.startTaskName))

        if not self.task == None:
            self.task()

        #emit signal after main loop
        if self.__close__ == False and self.params.finishTaskName:
            self.emit(SIGNAL(self.params.finishTaskName))

    def stop(self):
        self.__stop__ = True

    def isStopped(self):
        return self.__stop__

    def close(self):
        self.__stop__ = True
        self.__close__ = True

    def emitUpdateTask(self):
        if self.__stop__ == False and self.params.updateTaskName:
            self.__emit_update_counter__ = self.__emit_update_counter__ + 1

            # check if a sleep have to be set
            if not self.params.emit_update_sleep == None \
                and (self.params.emit_update_sleep_step == None or \
                     (self.__emit_update_counter__ \
                      & self.params.emit_update_sleep_step) == 0):
                self.msleep(self.params.emit_update_sleep)

            # check when emit a signal have to be issued
            if self.params.emit_update_step == None or \
                (self.__emit_update_counter__
                 & self.params.emit_update_step) == 0:
                self.emit(SIGNAL(self.params.updateTaskName))

    def setTask(self, task):
        self.task = task

    def getTask(self):
        return self.task

    def setUpdateTask(self, updateTaskName, updateAction):
        if not self.params.updateAction == None and self.params.updateTaskName:
            if self.params.updateAction == updateAction and \
                self.params.updateTaskName == updateTaskName:
                return
            self.disconnect(self, SIGNAL(self.params.updateTaskName),
                            self.params.updateAction)
        self.params.updateTaskName = updateTaskName
        self.params.updateAction = updateAction
        self.connect(self, SIGNAL(self.params.updateTaskName),
                         self.params.updateAction)

    def setFinishTask(self, finishTaskName, finishAction):
        if not self.params.finishAction == None and self.params.finishTaskName:
            if self.params.finishAction == finishAction and \
                self.params.finishTaskName == finishTaskName:
                return
            self.disconnect(self, SIGNAL(self.params.finishTaskName),
                            self.params.finishAction)
        self.params.finshTaskName = finishTaskName
        self.params.finishAction = finishAction
        self.connect(self, SIGNAL(self.params.finishTaskName),
                         self.params.finishAction)
