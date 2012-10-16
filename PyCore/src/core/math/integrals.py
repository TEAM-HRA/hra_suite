'''
Created on 19-08-2012

@author: jurek
'''
from pylab import find
from pylab import sum


class DefiniteIntegral(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    @staticmethod
    def integration(x, f, a, b):
        """This function accepts three arguments. x is the independent
        variable, f is the dependent variable,a and b are
        the limits of integration. The integral over the indicated period
        is returned"""

        index_down = find(x >= a)[0]
        index_up = find(x < b)[-1]

        return sum(f[index_down:index_up])
