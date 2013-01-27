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


def convert_file_specification(file_specification):
    data_index = int(file_specification.data_index)
    annotation_index = file_specification.annotation_index
    if not annotation_index == None and len(str(annotation_index)) == 0:
        file_specification = file_specification._replace(annotation_index=None,
                                                    data_index=data_index)
    else:
        file_specification = file_specification._replace(
                                        annotation_index=int(annotation_index),
                                        data_index=data_index)
    return file_specification
