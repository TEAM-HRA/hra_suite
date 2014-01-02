'''
Created on Dec 30, 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import os.path as fs
    import numpy as np
    import matplotlib.pyplot as plt
    from hra_core.collections_utils import nvl
    from hra_core.collections_utils import get_as_list
    from hra_core.collections_utils import get_chunks
    from hra_core.io_utils import get_first_lines
    from hra_core.io_utils import get_filename
    from hra_core.io_utils import as_path
except ImportError as error:
    print_import_error(__name__, error)


def create_many_plots(_source_file, headers, separator, window_size=None):
    """
    draws many plots base on data from _source_file and collection of headers
    grouped by a semicolon, elements in a group are separated by a comma
    """
    colors = ['red', 'green', 'blue', 'yellow', 'black', 'cyan', 'magenta']

    first_line = get_first_lines(_source_file)
    if len(first_line) == 0:
        return
    file_headers = [header.strip().lower()
            for header in first_line[0].split(separator)]
    for sub_headers in get_as_list(headers, separator=';'):
        labels = [label.strip().lower()
                  for label in get_as_list(sub_headers)]
        try:
            cols = tuple([file_headers.index(label) for label in labels])
        except ValueError:
            continue
        if separator == None:
            values = np.loadtxt(_source_file, skiprows=1, unpack=True,
                                usecols=cols)
        else:
            values = np.loadtxt(_source_file, skiprows=1, unpack=True,
                                usecols=cols, delimiter=separator)

        plt.gca().set_color_cycle(colors[:len(labels)])

        filename = get_filename(_source_file)
        title = "%s %s" % (filename, nvl(window_size + " window size", ''))
        plt.title(title)

        for value in values:
            plt.plot(value)

        plt.legend(labels, loc='upper right')
        plt.axes().set_xlabel('Time')

        plot_filename = "%s_%s.png" % (filename, '_'.join(labels))
        _file = as_path(fs.dirname(_source_file), plot_filename)
        plt.savefig(_file)
        plt.cla()
