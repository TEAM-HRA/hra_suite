'''
Created on 02-11-2012

@author: jurek
'''


class Context(object):
    """
    a class to store/retrieve various context parameters
    associated with a passed target which could be any kind of
    python object for example a public method of a class;
    the first usage of the Context class happened during application of
    slot methods which can be defined as static method calls in a external
    file; because signal/slot mechanism in QT demands the same amount of
    parameters in signals and slots interfaces, the Context class is used to
    passed any additional objects which could be utilize by a caller
    (the static method in our example)
    """

    def __init__(self, target):
        self.__target = target

    def save(self, **params):
        """
        save or attach parameters to self.__parent
        """
        for key in params.keys():
            setattr(self.__target, "__context__" + key, params.get(key, None))

    def __getattr__(self, name):
        return getattr(self.__target, "__context__" + name, None)

GlobalContext = Context(Context)
