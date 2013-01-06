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


def get_class_object(_class_dotted_name, default=None):
    return get_object(_class_dotted_name, default=default)


def get_method_member_object(_method_dotted_name, default=None):
    return get_object(_method_dotted_name, default=default)


def get_module_object(_module_dotted_name):
    return get_object(_module_dotted_name)


def get_object(name, default=None):
    """
    method which returns any member (class, method, function)
    included in a module and specified by a parameter name in
    a dot (package) format
    '<name1>.<name2>.[...].<name_n>'
    """
    splits = name.split(".")
    module_name = name
    level = 0
    #searching for a module
    while True:
        try:
            __import__(module_name, globals(), locals(), [], -1)
            break
        except (ImportError):
            level = level - 1
            module_name = __s(splits[:level])
            if len(module_name) == 0:
                return default
            else:
                continue

    from_name = __s(splits[level:])
    object_names = __import__(module_name, fromlist=[from_name])
    for name in splits[level:]:
        _object = getattr(object_names, name, None)
        if _object == None:
            break
        object_names = _object
    #print(str(_object))
    return default if _object == None else _object


def __s(_list):
    return ".".join(_list)
