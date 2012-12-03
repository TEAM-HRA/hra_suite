'''
Created on 03-12-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params


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
        if self.params.startAction:
            self.connect(self, SIGNAL(self.params.startTaskName),
                         self.params.startAction)
        if self.params.updateAction:
            self.connect(self, SIGNAL(self.params.updateTaskName),
                         self.params.updateAction)
        if self.params.finishAction:
            self.connect(self, SIGNAL(self.params.finishTaskName),
                         self.params.finishAction)

    def run(self):
        #counts how many emit update tasks are invoked
        self.__emit_update_counter__ = 0

        self.__stop__ = False
        self.__close__ = False

        #emit signal before main loop
        if self.params.startTaskName:
            self.emit(SIGNAL(self.params.startTaskName))

        self.run_task()

        #emit signal after main loop
        if self.__close__ == False and self.params.finishTaskName:
            self.emit(SIGNAL(self.params.finishTaskName))

        self.__stop__ = False
        self.__close__ = False

        self.__emit_update_counter__ = 0

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

    def run_task(self):
        """
        main thread task (loopy part of a thread),
        have to be implemented in a subclass
        """
        raise NotImplementedError()
