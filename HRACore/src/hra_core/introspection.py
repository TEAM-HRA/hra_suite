'''
Created on 24-10-2012

@author: jurek
'''

import inspect
from types import MethodType
from hra_core.collections_utils import get_as_list
from hra_core.misc import is_empty


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
        if not (getattr(_method, '__func__', None) == None
                 and getattr(_method, 'func_name', None) == None)\
        else -1


def get_subclasses_names(_class, remove_base_classname=False,
                                remove_name=None):
    """
    get all class _class subclasses names, with ability to remove
    a baseclass name in the outcome
    """
    names = []
    for _sub_class in get_subclasses(_class):
        name = _sub_class.__name__
        if remove_base_classname:
            idx = _sub_class.__name__.rfind(_class.__name__)
            if idx >= 0:
                name = name[:idx]
        if remove_name:
            idx = name.rfind(remove_name)
            if idx >= 0:
                name = name[:idx]
        names.append(name)
    return names


def __private_properties_accessor__(source, _handler, target=None):
    """
    method to get access to private source object properties,
    proper action is delegated to specified handler
    """
    members = inspect.getmembers(source)
    for (name, member) in members:
        if inspect.ismethod(member):
            continue
        if inspect.isfunction(member):
            continue
        if inspect.isclass(member):
            continue
        if inspect.isroutine(member):
            continue
        if inspect.isgeneratorfunction(member):
            continue
        if str(type(member)) == "<type 'method-wrapper'>":
            continue
        if name.startswith('__'):
            continue
        if target is not None:
            _handler(source, target, name)
        else:
            _handler(source, name)


def copy_private_properties(source, target):
    """
    method to copy private properties from one object to another
    """
    def handler(source, target, name):
        setattr(target, name, getattr(source, name))
    __private_properties_accessor__(source, handler, target=target)


def print_private_properties(source, not_empty=True, skip_prefix=None,
                            skip_uppercase=True):
    """
    method to print source's object private properties
    """
    def handler(source, name):
        value = getattr(source, name)
        if __correct_private_property__(name, value, not_empty, skip_prefix,
                                   skip_uppercase):
            print(name + ' = ' + str(value))
    __private_properties_accessor__(source, handler)


def save_private_properties(source, _file, not_empty=True, skip_prefix=None,
                            skip_uppercase=True):
    """
    method to save source's object field properties into a file
    """
    def handler(source, name):
        value = getattr(source, name)
        if __correct_private_property__(name, value, not_empty, skip_prefix,
                                   skip_uppercase):
            handler._file.write(name + ' = ' + str(value) + '\n')
    handler._file = _file
    __private_properties_accessor__(source, handler)


def __correct_private_property__(name, value, not_empty, skip_prefix,
                             skip_uppercase):
    """
    check some conditions for print_private_properties, save_private_properties
    functions
    """
    if not skip_prefix == None and name.startswith(skip_prefix):
        return False
    elif skip_uppercase and name == name.upper():
        return False
    else:
        if not_empty and is_empty(value):
            return False
        elif hasattr(value, '__getattr__'):
            return False
        else:
            return True


def get_subclasses_iter(_class, seen=None, depth=-1):
    """
    method returns iterator of all subclasses of a class _class
    """
    if depth == 0:
        return
    depth -= 1
    if not isinstance(_class, type):
        raise TypeError('Parameter _class ' + str(_class) + ' has to be a type') # @IgnorePep8
    if seen == None:
        seen = []
    try:
        subs = _class.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = _class.__subclasses__(_class)
    for sub in subs:
        if sub not in seen:
            seen.append(sub)
            yield sub
            for sub in get_subclasses_iter(sub, seen, depth):
                yield sub


def get_subclasses(_class, depth=-1):
    return list(get_subclasses_iter(_class, depth=depth))


def get_child_of_type(parent_object, child_type,
                      children_method_name="children"):
    children_method = getattr(parent_object, children_method_name)
    for child in children_method():
        if isinstance(child, child_type):
            return child


def expand_to_real_class_names(short_classes_names, _base_class,
                               _class_suffix=''):
    """
    method converts user's inputed classes names into
    real statistics class names
    e.g. _class_suffix = 'statistic'
    """
    real_classes_names = []
    real_names = [(name, name.lower(), )
                    for name in get_subclasses_names(_base_class)]
    lower_names = [(name.lower(), name.lower() + _class_suffix, )  # e.g. _class_suffix = 'statistic' @IgnorePep8
                   for name in get_as_list(short_classes_names)]
    for (class_lower_name, class_base_name) in lower_names:
        for (real_name, real_lower_name) in real_names:
            if real_lower_name in (class_lower_name, class_base_name):
                real_classes_names.append(real_name)
                break
        else:
            print('Uknown class: ' + class_lower_name)
            return []
    return real_classes_names


def get_subclasses_names_with_suffix(_class, only_short_names=False,
                                      short_name_suffix=None):
    """
    method returns names of subclasses without short name suffix
    """
    names = sorted([subclass.__name__ for subclass in get_subclasses(_class)])
    if short_name_suffix == None:
        short_name_suffix = _class.__name__
    if only_short_names:
        return [name[:name.rfind(short_name_suffix)] for name in names]
    else:
        return names
