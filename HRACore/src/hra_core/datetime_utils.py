'''
Created on Jun 30, 2013

@author: jurek

module used for some specific tasks concerning time and date
'''
import datetime


class DateTimeUtils(object):
    """
    class with some useful time/date functionality
    """

    def __init(self):
        self.__start_datetime__ = datetime.datetime.now()
        self.__stop_datetime__ = self.__start_datetime__

    def start_now(self):
        self.__start_datetime__ = datetime.datetime.now()

    def stop_now(self):
        self.__stop_datetime__ = datetime.datetime.now()

    @property
    def difference_as_string(self):
        difference_delta = self.__stop_datetime__ - self.__start_datetime__
        hours, remainder = divmod(difference_delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return 'h:%d, m:%02d, s:%02d' % (hours, minutes, seconds)


def invocation_time(method):
    """
    decorator function used to measure execution of a function/method
    """

    def datetime_wrapper(_self, *args, **kw):
        date_time_utils = DateTimeUtils()
        date_time_utils.start_now()
        result = method(_self, *args, **kw)
        date_time_utils.stop_now()
        print("Duration: [%s] " % date_time_utils.difference_as_string)
        return result

    return datetime_wrapper


def get_time_label_for_miliseconds(miliseconds):
    time_ = get_time_for_miliseconds(miliseconds)
    return 'H : %02d, M : %02d, S : %02d' % time_


def get_time_label_parts_for_miliseconds(miliseconds):
    time_ = get_time_for_miliseconds(miliseconds)
    return ('H:%02d' % time_[0], 'M:%02d' % time_[1], 'S:%02d' % time_[2])


def get_time_for_miliseconds(miliseconds):
    hours, remainder = divmod(miliseconds / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (hours, minutes, seconds)


def __format_as_datetime__(_s_datetime):
    """
    function used internally to convert string datetime into
    real datetime object
    """
    f = __format_as_datetime__._format
    return datetime.datetime.strptime(_s_datetime, f)


def convert_strings_to_datetimes(iterator, _format):
    """
    function converts iterator of strings into datetime objects,
    example _format specification:
    '%H:%M:%S.%f' <=> "08:21:44.020"
    """
    __format_as_datetime__._format = _format
    return map(__format_as_datetime__, iterator)


def get_miliseconds_from_timedelta(tdelta):
    return tdelta.seconds * 1000 + tdelta.microseconds / 1000
