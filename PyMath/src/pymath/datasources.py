'''
Created on 15-08-2012

@author: jurek
'''
import glob
import os
from re import findall
from numpy import array
from numpy import loadtxt
from pycore.globals import NUMPY_USAGE


class DataSource(object):

    def __init__(self, signal=None, annotation=None):
        '''
        Constructor
        '''
        if (isinstance(signal, DataSource)):
            self.signal = signal.signal
            self.annotation = signal.annotation
        else:
            self.signal = signal
            self.annotation = annotation

    @property
    def signal(self):
        return self.__signal__

    @signal.setter
    def signal(self, signal):
        self.__signal__ = signal

    @property
    def annotation(self):
        return self.__annotation__

    @annotation.setter
    def annotation(self, anntotation):
        self.__annotation__ = anntotation

    def __str__(self):
        return (self.__for_str__('signal', self.signal) + ' '
              + self.__for_str__('annotation', self.annotation))

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
        self.header = header
        self.num = -1

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
        self.__cols__ = []

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
                    self.__cols__.append(num)
                    break
        return spec

    def __iter__(self):
        return self

    def next(self):
        if self.__filenames__ and len(self.__filenames__) > self.__idx__:
            self.__idx__ += 1
            filename = self.__filenames__[self.__idx__ - 1]
            if NUMPY_USAGE:
                return self.__getNumPyDataSource__(filename)
            else:
                return self.__getDataSource__(filename)
        else:
            raise StopIteration

    @property
    def headers(self):
        if not self.__headers__:
            with open(self.__filenames__[0], 'r') as _file:
                header_line = _file.readline()  # header line
                self.__headers__ = findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', header_line) #@IgnorePep8
        return self.__headers__

    def __getDataSource__(self, filename):
        signal = []
        annotation = []

        with open(filename, 'r') as _file:
            _file.readline()  # skip header line
            for line in _file:
                contents = findall(r'\b[0-9\.]+', line)
                if self.signal_spec:
                    signal.append(float(contents[self.signal_spec.num]))
                if self.annotation_spec:
                    annotation.append(int(float(contents[self.annotation_spec.num]))) #@IgnorePep8

        return self.__createDataSource__(filename, array(signal), array(annotation)) #@IgnorePep8

    @property
    def signal_spec(self):
        return self.__signal_spec__

    @property
    def annotation_spec(self):
        return self.__annotation_spec__

    @property
    def cols(self):
        return self.__cols__

    def __getNumPyDataSource__(self, filename):
        signal = None
        annotation = None

        if len(self.cols) == 2:
            (signal, annotation) = loadtxt(filename,
                                           skiprows=1,
                                           usecols=self.cols,
                                           unpack=True)
            annotation = annotation.astype(int)
        else:
            signal = loadtxt(filename,
                             skiprows=1,
                             usecols=self.cols,
                             unpack=True)

        return self.__createDataSource__(filename, signal, annotation)

    def __createDataSource__(self, filename, signal, annotation):
        if (self.annotation_spec and self.signal_spec
            and self.signal_spec.num == self.annotation_spec.num):
            annotation = 0 * signal

        data_source = DataSource(signal, annotation)
        data_source.filename = filename  # set up an additional property
        return data_source