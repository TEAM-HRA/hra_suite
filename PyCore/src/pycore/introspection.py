'''
Created on 24-10-2012

@author: jurek
'''

import inspect
from types import MethodType


def hasSuperclass(target, superclass_name):
    tclass = target.__class__
    for base_type in inspect.getmro(
                target if tclass.__name__ == 'type' else tclass):
        if base_type.__name__ == superclass_name:
            return True
    return False


def addInstanceMethod(_new_method, _class, _method_name, _object=None):
    """
    add a method, named by _method_name, (references by _new_method) during
    runtime to an object (if _object is not None) or the whole class
    (references by _class_)
    """
    setattr(_class, _method_name, MethodType(_new_method, _object, _class))
    # _class.method = MethodType(_new_method, _object, _class)


#def arguments():
#        """Returns tuple containing dictionary of calling function's
#           named arguments and a list of calling function's unnamed
#           positional arguments.
#        """
#        from inspect import getargvalues, stack
#        posname, kwname, args = getargvalues(stack()[1][0])[-3:]
#        posargs = args.pop(posname, [])
#        args.update(args.pop(kwname, []))
#        return args, posargs

class ProxyType(object):
    """
    class which could be use to create a proxy objects
    """
    def __init__(self, host_object):
        for attr in dir(host_object):
            name = str(attr)
            if name == '__weakref__':
                continue
            setattr(self, name, getattr(host_object, name))


def get_class_object(_class_dotted_name):
    return ObjectGenerator(_class_dotted_name).getClass()


def get_method_member_object(_method_dotted_name):
    return ObjectGenerator(_method_dotted_name).getMethod()


class ObjectGenerator(object):

    def __init__(self, _object_dotted_name):
        """
        object name in a dotted (package) form:
        '<name1>.<name2>...<name_n>.<class_name>[.<method_name>]'
        """
        self.__object_dotted_name__ = _object_dotted_name

    def getModule(self, shift=2):
        self.__shift__ = shift
        return __import__(self.__package, fromlist=[self.__class])

    def getClass(self, shift=1):
        _module_ = self.getModule(shift)
        if _module_:
            return getattr(_module_, self.__class, None)

    def getMethod(self, shift=0):
        _class_object = self.getClass(shift)
        if _class_object:
            return getattr(_class_object, self.__method, None)

    @property
    def __method(self):
        return self.__part(-1 + self.__shift__)

    @property
    def __class(self):
        return self.__part(-2 + self.__shift__)

    @property
    def __module(self):
        return self.__part(-3 + self.__shift__)

    @property
    def __package(self):
        return self.__part(0, -2 + self.__shift__)

    def __part(self, start, end=None):
        splits = self.__object_dotted_name__.split(".")
        return splits[start] if end == None else ".".join(splits[start:end])
