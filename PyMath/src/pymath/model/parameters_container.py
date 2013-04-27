'''
Created on 26 kwi 2013

@author: jurek
'''


class ParametersContainer(object):
    """
    class used to hold all parameters objects which are used
    during processing poincare plot
    """

    def __init__(self):
        self.__parameters__ = {}

    @property
    def parameters(self):
        return self.__parameters__

    def getParametersObject(self, _name, _class):
        parameters_object = self.__parameters__.get(_name, None)
        if parameters_object == None:
            parameters_object = _class()
            self.__parameters__[_name] = parameters_object
        return parameters_object
