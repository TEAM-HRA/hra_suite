'''
Created on 26-01-2013

@author: jurek
'''


def print_import_error(_module, _error):
    print('import error: ' + str(_error) + ' in module: ' + str(_module))

try:
    import inspect
except ImportError as error:
    print_import_error(__name__, error)


def get_values_as_map(_object, with_none=False, only_simple_type_values=True):
    _list = []
    for method in get_members_names(_object.__class__):
        if with_none or not getattr(_object, method, None) == None:
            value = getattr(_object, method, None)
            if only_simple_type_values and hasattr(value, '__len__'):
                continue  # skip composite elements
            _list.append((method, value))
    return dict(_list)


def get_members_names(_object_class):
    return [method for (method, _)  in inspect.getmembers(_object_class)
                    if not method.startswith('__')]


#this variable is set up by external code, too
USE_NUMPY_EQUIVALENT = True
