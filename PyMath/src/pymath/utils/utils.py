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


def get_values_as_map(_object, with_none=False):
    return dict([(method, getattr(_object, method, None))
                for method in get_members_names(_object.__class__)
                if with_none or not getattr(_object, method, None) == None])


def get_members_names(_object_class):
    return [method for (method, _)  in inspect.getmembers(_object_class)
                    if not method.startswith('__')]


#this variable is set up by external code, too
USE_NUMPY_EQUIVALENT = True


class Params(object):
    """
    class which represents dictionary parameters
    by object where elements are accessible with dot notation
    if client tries to access not existing element then None value is returned
    """
    def __init__(self, **params):
        for param in params:
            setattr(self, param, params[param])

    # if parameter is not set in the __init__() method then returns None
    def __getattr__(self, name):
        return None
