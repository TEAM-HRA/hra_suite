'''
Created on 23-07-2012

@author: jurek
'''

from re import findall


def getIndexForValue(collection, value):
    return binarySearch(collection, value)


def getAsTypedCollection(string, substringType):
    if isinstance(substringType, int.__class__):
        return findall(r'\b[0-9]+\b', string)
    elif isinstance(substringType, float.__class__):
        return findall(r'\b[0-9]+\.[0-9]+\b', string)
    else:
        return findall(r'\b.*\b', string)


def binarySearch(collection, value, left=0, right=None):
    """
    Iterative binary search function
    collection:
        can be any iterable object
    """
    if right is None:
        # if max amount not set, get the total
        right = len(collection) - 1

    while left <= right:
        # calculate the midpoint
        mid = (left + right) // 2
        midval = collection[mid]

        # determine which subarray to search
        if midval < value:
            # change min index to search upper subarray
            left = mid + 1
        elif midval > value:
            # change max index to search lower subarray
            right = mid - 1
        else:
            # return index number
            return mid
    raise ValueError
