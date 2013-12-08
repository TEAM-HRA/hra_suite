'''
Created on Nov 2, 2013

@author: jurek
'''

import pylab as pl
import datetime

#_file = "/home/jurek/volumes/doctoral/monitor_do_impedancji_niccomo/_healthy/test.res" #
#
#
##dtype = {'names': ('time', 'ACI', 'ACIx'), 'formats': ('S13', 'S3', 'S3')}
##dtype = {'names': ('time'), 'formats': ('S13')}
#dtype = (str)
#
#_d = pl.loadtxt(_file, dtype=dtype, skiprows=2, unpack=True) # , comments, delimiter, converters, skiprows, usecols, unpack, ndmin)
#x = 0
#print(type(_d))
#print(_d)
#for _d1 in _d:
#    print(_d1, type(_d1), len(_d1), _d1[0], _d1[1], _d1[2])
#    x += 1
#    if x == 3:
#        break


#def data_decorator(fn):
#    def wrapped(_self=None):
#        _data = fn(_self)
#        print('IN WRAPPER  _data: ' + str(_data))
#        _self.setData(_data)
#        return _data
#    return wrapped
#
#
#class ClassBase(object):
#    def __init__(self):
#        self._data = None
#
#    def setData(self, _data):
#        self._data = _data
#
#    def isData(self):
#        return not self._data == None
#
#    @staticmethod
#    def dataDecorator(fn):
#        def wrapped(_self=None):
#            _data = fn(_self)
#            print('IN dataDecorator  _data: ' + str(_data))
#            _self.setData(_data)
#            return _data
#        return wrapped
#
#
#class ClassA(ClassBase):
#    def __init__(self):
#        pass
#
#    # @ data_decorator
#    @ClassBase.dataDecorator
#    def getData(self):
#        return "My value"

#aa = ClassA()
#print(aa.getData())
#print(aa.isData())


#def difference_in_micr
#s1 = "08:21:44.020"
#d1 = datetime.strptime(s1, '%H:%M:%S.%3f')
#s2 = "08:21:44.870"
#d2 = datetime.strptime(s2, '%H:%M:%S.%3f')
#(d2 -d1).microseconds /100


#def convert_str_to_datetime(_value):
#    f = convert_str_to_datetime._format
#    #datetime.strptime(_value, '%H:%M:%S.%f')
#    return datetime.strptime(_value, f)
#
#convert_str_to_datetime._format = '%H:%M:%S.%f'
#
#a2 = pl.array(["08:21:44.020", "08:21:44.870"])
#dd = pl.array(map(convert_str_to_datetime, a2))
#print(type(dd))
#print(dd)


def __format_as_datetime__(_value):
    f = __format_as_datetime__._format
    #datetime.strptime(_value, '%H:%M:%S.%f')
    return datetime.datetime.strptime(_value, f)
#def difference_in_micr
#s1 = "08:21:44.020"
#d1 = datetime.strptime(s1, '%H:%M:%S.%3f')
#s2 = "08:21:44.870"
#d2 = datetime.strptime(s2, '%H:%M:%S.%3f')
#(d2 -d1).microseconds /100


def convert_strings_to_datetimes(iterator, _format):
    """
    function converts iterator of strings into datetime objects,
    example format specification:
    '%H:%M:%S.%f' => "08:21:44.020"
    """
    __format_as_datetime__._format = _format
    return map(__format_as_datetime__, iterator)


#s1 = "08:21:44.020"
#d1 = datetime.datetime.strptime(s1, '%H:%M:%S.%f')
#s2 = "08:21:44.870"
#d2 = datetime.datetime.strptime(s2, '%H:%M:%S.%f')
#ddelta = d2 - d1
#dds = pl.array([s1, s2])
#print(type(ddelta))


def get_miliseconds_from_timedelta(tdelta):
    #print(dir(tdelta))
    print('tdelta.seconds', tdelta.seconds)
    print('tdelta.total_seconds', tdelta.total_seconds)
    return tdelta.seconds * 1000 + tdelta.microseconds / 1000


def get_datetimes_array_as_intervals(datetimes, _format):
    if not datetimes == None and len(datetimes) > 0:
        if isinstance(datetimes[0], str):
            datetimes = pl.array(
                            convert_strings_to_datetimes(datetimes, _format))
        deltas = datetimes[1:] - datetimes[:-1]
        miliseconds = map(get_miliseconds_from_timedelta,
                                             deltas)
        return pl.array(miliseconds)
    return datetimes if isinstance(datetimes, pl.array) \
                        else pl.array(datetimes)


#def __get_time_as_miliseconds_segments__(self, time):
#    """
#    change time array expressed in datetime units
#    into miliseconds periods;
#    returned array is less by one then parameter time array
#    """
#    if not time == None:
#        datetime_array = pl.array(
#                            convert_str_to_datetime(time, '%H:%M:%S.%f'))
#        start_datetime_array = datetime_array[:-1]
#        end_datetime_array = datetime_array[1:]
#        segments = end_datetime_array - start_datetime_array
#        #map()
#        return (end_datetime_array - start_datetime_array).microseconds / 1000 # @IgnorePep8


#print(convert_str_to_datetime(dds, '%H:%M:%S.%f'))

#datetimes = pl.array(["08:21:44.020", "08:21:44.870", "08:21:45.550", "08:21:45.900", "08:21:46.333"])
datetimes = pl.array(['08:21:38.010', '08:21:44.020'])

datetimes = get_datetimes_array_as_intervals(datetimes, '%H:%M:%S.%f')
print(datetimes)

