'''
Created on 9 kwi 2013

@author: jurek
'''


class Filter(object):
    '''
    base class (in a role of abstract class) for filters
    '''

    def __init__(self, _shift=1, **params):
        '''
        Constructor
        '''
        self.__shift__ = _shift

    def check(self, _data_vector):
        """
        method returns None if a filter will be used or a text message
        if not be used due to specific data conditions
        """
        pass

    def filter(self, _data_vector):
        return self.__filter__(_data_vector)

    def __filter__(self, _data_vector):
        return _data_vector
