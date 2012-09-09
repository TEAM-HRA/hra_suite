'''
Created on 15-08-2012

@author: jurek
'''
import glob
import os
from re import findall
from numpy import array


class DataSource(object):

    def __init__(self, data_source=None, _annotation=None):
        '''
        Constructor
        '''
        if (isinstance(data_source, DataSource)):
            self.__signal__ = data_source.__signal__
            self.__annotation__ = data_source.__annotation__
        else:
            self.__signal__ = data_source
            self.__annotation__ = _annotation

    @property
    def signal(self):
        return self.__signal__

    @signal.setter
    def signal(self, _signal):
        self.__signal__ = _signal

    @property
    def annotation(self):
        return self.__annotation__

    @annotation.setter
    def annotation(self, _anntotation):
        self.__annotation__ = _anntotation

    def __str__(self):
        return (self.__for_str__('signal', self.__signal__) + ' '
              + self.__for_str__('annotation', self.__annotation__))

    def __for_str__(self, prefix, data):
        if hasattr(data, 'take') or hasattr(data, '__getslice__'):
            l = len(data)
            if hasattr(data, 'take'):
                sample = data.take(range(10 if l > 10 else l))
            elif hasattr(data, '__getslice__'):
                sample = data[0:(10 if l > 10 else l)]
            return ("{0} [size {1} sample {2}] ".format(prefix, l, sample))
        return ''


class ColumnSpec(object):
    def __init__(self, header):
        self.__header__ = header
        self.__num__ = -1

    @property
    def num(self):
        return self.__num__

    @num.setter
    def num(self, num):
        self.__num__ = num

    @property
    def header(self):
        return self.__header__

    @header.setter
    def header(self, header):
        self.__header__ = header


class AnnotationColumnSpec(ColumnSpec):
    pass


class SignalColumnSpec(ColumnSpec):
    pass


class FilesDataSources(object):

    def __init__(self, path, ext=None):

        self.__idx__ = 0
        self.__headers__ = []
        self.__filenames__ = []
        self.__signal_spec__ = None
        self.__annotation_spec__ = None

        path = path + ('*.*' if ext == None else ext)
        for filename in glob.glob(path):
            if os.path.isfile(filename):
                self.__filenames__.append(filename)

    def setColumnsSpecs(self, signal_spec, annotation_spec):
        self.__signal_spec__ = self.__fillNum__(signal_spec)
        self.__annotation_spec__ = self.__fillNum__(annotation_spec)

    def __fillNum__(self, spec):
        if spec:
            spec.num = None
            for num, header in enumerate(self.headers, start=0):
                if spec.header == header:
                    spec.num = num
                    break
        return spec

    def __iter__(self):
        return self

    def next(self):
        if self.__filenames__ and len(self.__filenames__) > self.__idx__:
            self.__idx__ += 1
            return self.__getDataSource__(self.__idx__ - 1)
        else:
            raise StopIteration

    @property
    def headers(self):
        if not self.__headers__:
            with open(self.__filenames__[0], 'r') as _file:
                first_line = _file.readline()  # header line
                self.__headers__ = findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', first_line) #@IgnorePep8
        return self.__headers__

    def __getDataSource__(self, idx):
        signal = []
        annotation = []

        with open(self.__filenames__[idx], 'r') as _file:
            _file.readline()  # skip header line
            for line in _file:
                contents = findall(r'\b[0-9\.]+', line)
                if self.__signal_spec__:
                    signal.append(float(contents[self.__signal_spec__.num]))
                if self.__annotation_spec__:
                    annotation.append(int(float(contents[self.__annotation_spec__.num]))) #@IgnorePep8

        if (self.__annotation_spec__ and self.__signal_spec__
            and self.__signal_spec__.num == self.__annotation_spec__.num):
            annotation = 0 * signal

        data_source = DataSource(array(signal), array(annotation))
        data_source.filename = self.__filenames__[idx]
        return data_source
