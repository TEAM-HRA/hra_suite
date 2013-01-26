'''
Created on 26-01-2013

@author: jurek
'''
import collections

FileSpecification = collections.namedtuple('FileSpecification',
    ["filepath", "filename", "data_index", "annotation_index", "separator"])
