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


def get_object(name, default=None, level=0):
    """
    method which returns any member (class, static method, function)
    included in a module and specified by a parameter name in
    a dot (package) format
    '<name1>.<name2>.[...].<name_n>'
    the function works in recursive manner
    """
    splits = name.split(".")

    #if level == 0 that means we have to search a module as
    #a name parameter, if level < 0 then one level downward
    #for example if name = 'a.b.c.d.e' then for level == -1
    #module_name = 'a.b.c.d', for level = -2 name_module = 'a.b.c' etc
    module_name = name if level == 0 else __s(splits[:level])

    #there is no module name so there is nothing to search
    if len(module_name) == 0:
        return default

    #fromlist is a part of name parameter after module name
    #for example:
    #name = 'a.b.c.d.e', module_name = 'a.b.c' (level = -2)
    #then fromlist = ['d.e']
    fromlist = [] if level == 0 else [__s(splits[level:])]

    #try to import module dynamically
    _object = None
    try:
        _object = __import__(module_name, fromlist=fromlist)
    except (ImportError):
        pass

    if not _object == None:
        #walks through elements after module name, for example:
        #if name = 'a.b.c.d.e' and module_name = 'a.b.c' (level = -2)
        #then split_name gets values: d, e
        #the below loop tries to get attributes of object _object
        #goes from object represents a module into the last element
        #of the name attribute downward
        for split_name in splits[level:]:
            _object = getattr(_object, split_name, None)
            if _object == None:
                break

    #if _object is None we have to search for one level downward
    return get_object(name, default, level=level - 1) \
            if _object == None else _object


def __s(_list):
    return ".".join(_list)


def create_class_object_with_suffix(_class_package, _class_name, _suffix=None):
    """
    method creates class object using passed _class_package, _class_name
    and with _suffix if it is present
    """
    #check if a name is not in dot format
    if not _class_name.rfind('.') >= 0:
        #append a _suffix suffix if not present already
        if _suffix and not _class_name.endswith(_suffix):
            _class_name += _suffix
        #prefix with current package
        full_class_name = '.'.join([_class_package, _class_name])
    class_object = get_class_object(full_class_name)
    if class_object == None:
        raise TypeError("class " + full_class_name + " doesn't exist")
    else:
        return class_object


def get_method_arguments_count(_method):
    """
    method returns number of parameters of passed _method
    """
    return len(inspect.getargspec(_method).args) \
        if hasattr(_method, '__func__') or hasattr(_method, 'func_name') \
        else -1


def get_subclasses_short_names(_class, remove_base_classname=False):
    """
    get all class _class subclasses names, with ability to remove
    a baseclass name in the outcome
    """
    names = []
    for _sub_class in _class.__subclasses__():
        name = _sub_class.__name__
        if remove_base_classname:
            idx = _sub_class.__name__.rfind(_class.__name__)
            if idx >= 0:
                name = name[:idx]
        names.append(name)
    return names


def copy_object(source, target):
    """
    method to copy not private properties from one object to another
    """
    names = [name for name in dir(source) if not name[:2] == "__" and hasattr(target, name)]  # @IgnorePep8
    for name in names:
        setattr(target, name, getattr(source, name))
