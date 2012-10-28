'''
Created on 24-10-2012

@author: jurek
'''

import inspect


def hasSuperclass(target, superclass_name):
    tclass = target.__class__
    for base_type in inspect.getmro(
                target if tclass.__name__ == 'type' else tclass):
        if base_type.__name__ == superclass_name:
            return True
    return False
