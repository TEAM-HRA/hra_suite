'''
Created on 09-09-2012

@author: jurek
'''


import optparse

parser = optparse.OptionParser()
parser.add_option("-n", "--numpy_usage", type="string")
parser.set_default("numpy_usage", "true")
opts, args = parser.parse_args()

NUMPY_USAGE = (opts.numpy_usage == "true")
