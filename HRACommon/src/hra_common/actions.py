'''
Created on 15-01-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from hra_core.misc import Params
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ActionSpec(object):

    def __init__(self, **params):
        self.params = Params(**params)
        self.__iconId = self.params.iconId
        self.__tipId = self.params.tipId
        self.__signal = self.params.signal
        self.__slot = self.params.handler
        self.__title = self.params.title
        self.__checkable = ("True" == str(self.params.checkable))

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
    def checkable(self):
        return self.__checkable

    @checkable.setter
    def checkable(self, _checkable):
        self.__checkable = _checkable

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

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, _title):
        self.__title = _title
