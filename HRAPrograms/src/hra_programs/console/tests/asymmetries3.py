'''
Created on Nov 25, 2013

@author: jurek
'''
import sys
import os.path as fs
sys.path.append('/ssd_dev/git_repos/HRA/HRAMath/src')
sys.path.append('/ssd_dev/git_repos/HRA/HRACore/src')
from hra_core.io_utils import as_path
import hra_math.time_domain.poincare_plot.poincare_plot as poincare

root_dir = '/home/jurek/volumes/doctoral/monitor_do_impedancji_niccomo/'
result_dir = 'results_whole_for_R'
groups = ['_healthy', '_team']
#groups = ['_healthy']
parameters = ['SV', 'SVR', 'CO', 'PEP', 'LVET']
#parameters = ['SV']
#types = ['sliding', 'jumping']
#types = ['jumping']
types = ['whole']

for group in groups:
    for parameter in parameters:
        for _type in types:

            base_output_dir = as_path(root_dir, result_dir, group, _type) + fs.sep # @IgnorePep8

            #parameters
            parameter_dir = as_path(base_output_dir, parameter) + fs.sep
            pp = poincare.PoincarePlotManager()
            #if not _type == None:
            #pp.window_size = '5m'
            #pp.data_file = as_path(root_dir, group, '001.res')
            pp.data_dir = as_path(root_dir, group) + fs.sep
            pp.output_dir = parameter_dir
            pp.signal_label = parameter
            pp.time_label = 'time'
            pp.extension = '*.res'
            pp.statistics_names = 'sd1, sd2, sd1d, sd1a, sd2d, sd2a, sdnnd, sdnna, sdnn, c1d, c1a, c2a, c2d, ca, cd' # @IgnorePep8
            pp.output_separator = ';  '
            pp.override_existing_outcomes = True
            pp.headers_count = 2
            pp.time_format = '%H:%M:%S.%f'
            pp.print_first_signal = True
            pp.progress_mark = True
            #if _type == "jumping":
            #    pp.stepper = '5m'
            pp.generate()

#            #asymmetries
#            asymmetry_dir = as_path(base_output_dir, parameter + "_asymmetry") + fs.sep # @IgnorePep8
#            pp = poincare.PoincarePlotManager()
#            pp.data_dir = parameter_dir
#            pp.output_dir = asymmetry_dir
#            pp.signal_label = 'Asymmetry'
#            pp.extension = '*.res_out'
#            pp.statistics_names = 'mean'
#            pp.output_separator = ';  '
#            pp.separator = ';'
#            pp.override_existing_outcomes = True
#            pp.headers_count = 1
#            pp.print_first_signal = True
#            pp.progress_mark = True
#            pp.generate()
#
#            #means
#            means_dir = as_path(base_output_dir, "means") + fs.sep
#            pp = poincare.PoincarePlotManager()
#            pp.data_dir = asymmetry_dir
#            pp.group_data_filename = parameter + '_mean'
#            pp.output_dir = means_dir
#            pp.signal_label = 'mean'
#            pp.extension = '*.res_out_out'
#            pp.statistics_names = 'mean'
#            pp.output_separator = ';  '
#            pp.separator = ';'
#            pp.override_existing_outcomes = True
#            pp.headers_count = 1
#            pp.print_first_signal = True
#            pp.progress_mark = True
#            #pp.print_members()
#            pp.generate()
