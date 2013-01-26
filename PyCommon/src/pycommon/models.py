'''
Created on 26-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
except ImportError as error:
    ImportErrorMessage(error, __name__)

FileSpecification = collections.namedtuple('FileSpecification',
    ["pathname", "filename", "data_index", "annotation_index", "separator"])

FilePath = collections.namedtuple('FilePath', ["pathname", "filename"])
