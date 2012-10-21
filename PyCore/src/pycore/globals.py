'''
Created on 09-09-2012

@author: jurek
'''
import optparse

parser = optparse.OptionParser()
parser.add_option("-n", "--numpy_usage", type="string")
parser.set_default("numpy_usage", "true")

parser.add_option("-d", "--dir_data", type="string")
parser.add_option("-e", "--ext_mask", type="string")
parser.add_option("-p", "--program_dir", type="string")

opts, args = parser.parse_args()


DIR_DATA = opts.dir_data
EXT_MASK = opts.ext_mask
PROGRAM_DIR = opts.program_dir
NUMPY_USAGE = (opts.numpy_usage == "true")
