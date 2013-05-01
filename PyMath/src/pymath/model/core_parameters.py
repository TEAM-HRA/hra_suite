'''
Created on 27 kwi 2013

@author: jurek
'''


class CoreParameters(object):
    """
    this class is used as a based class for all parameters classes
    used during generation of poincare plots
    """

    (LOW_CHECK_LEVEL, MEDIUM_CHECK_LEVEL, NORMAL_CHECK_LEVEL) = (-1, 0, 1)

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None
