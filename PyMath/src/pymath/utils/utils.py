'''
Created on 26-01-2013

@author: jurek
'''
import inspect
import optparse


def get_values_as_map(_object, with_none=False):
    return dict([(method, getattr(_object, method, None))
                for method in get_members_names(_object.__class__)
                if with_none or not getattr(_object, method, None) == None])


def get_members_names(_object_class):
    return [method for (method, _)  in inspect.getmembers(_object_class)
                    if not method.startswith('__')]


def print_import_error(_module, _error):
    pass

__parser = optparse.OptionParser()
__parser.add_option("-n", "--use_numpy_equivalent", default=True)
__opts, __args = __parser.parse_args()

USE_NUMPY_EQUIVALENT = __opts.numpy_equivalent
