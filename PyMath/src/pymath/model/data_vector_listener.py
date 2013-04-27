'''
Created on 24 kwi 2013

@author: jurek
'''


class DataVectorListener(object):
    """
    optional listener used when there are some changes in data vector
    to do specific actions
    """
    def changeSignal(self, _signal, **params):
        pass

    def changeAnnotation(self, _annotation, **params):
        pass

    def changeXSignalUnit(self, _signal_unit, **params):
        pass

    def prepareParameters(self, data_vector_accessor):
        """
        method used to set up some parameters objects
        """
        pass
