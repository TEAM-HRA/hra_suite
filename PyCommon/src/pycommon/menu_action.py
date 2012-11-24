'''
Created on 20-10-2012

@author: jurek
'''


class Action(object):
    CHECKABLE = "checkable"

    def __init__(self):
        self.__iconId = None
        self.__tipId = None
        self.__type = None
        self.__signal = None
        self.__slot = None

    @property
    def iconId(self):
        return self.__iconId

    @iconId.setter
    def iconId(self, _iconId):
        self.__iconId = _iconId

    @property
    def tipId(self):
        return self.__tipId

    @tipId.setter
    def tipId(self, _tipId):
        self.__tipId = _tipId

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, _type):
        self.__type = _type

    @property
    def signal(self):
        return self.__signal

    @signal.setter
    def signal(self, _signal):
        self.__signal = _signal

    @property
    def slot(self):
        return self.__slot

    @slot.setter
    def slot(self, _slot):
        self.__slot = _slot
