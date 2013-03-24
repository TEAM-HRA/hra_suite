'''
Created on 26-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    from pycore.misc import is_empty
except ImportError as error:
    ImportErrorMessage(error, __name__)

FileSpecification = collections.namedtuple('FileSpecification',
    ["pathname", "filename",
     "signal_index", "annotation_index", "time_index", "separator",
     "signal_unit_class_name"])

FilePath = collections.namedtuple('FilePath', ["pathname", "filename"])


def convert_file_specification(file_specification):
    (signal_index, annotation_index, time_index) = \
        [(None if is_empty(str(index)) else int(index)) \
         for index in [file_specification.signal_index,
                      file_specification.annotation_index,
                      file_specification.time_index]]

    file_specification = file_specification._replace(
                                        annotation_index=annotation_index,
                                        signal_index=signal_index,
                                        time_index=time_index)
    return file_specification
