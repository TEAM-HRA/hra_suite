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


def create_2_plots(_source_file, headers, separator, window_size=None):
    """
    draw to plots base on data from _source_file and collection of headers
    identifiers separated by comma and grouped by 2
    """
    first_line = get_first_lines(_source_file)
    if len(first_line) == 0:
        return
    file_headers = [header.strip().lower()
            for header in first_line[0].split(separator)]
    for (label1, label2) in map(tuple, get_chunks(get_as_list(headers),
                                                  chunk_size=2)):
        label1 = label1.strip().lower()
        label2 = label2.strip().lower()
        try:
            col1 = file_headers.index(label1)
            col2 = file_headers.index(label2)
        except ValueError:
            continue
        if separator == None:
            values1, values2 = np.loadtxt(_source_file, skiprows=1,
                                          unpack=True, usecols=(col1, col2))
        else:
            values1, values2 = np.loadtxt(_source_file, skiprows=1,
                                        delimiter=separator,
                                        unpack=True, usecols=(col1, col2))

        plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])

        filename = get_filename(_source_file)
        title = "%s %s" % (filename, nvl(window_size + " window size", ''))
        plt.title(title)

        plt.plot(values1)
        plt.plot(values2)

        plt.legend([label1, label2], loc='upper left')
        plt.axes().set_xlabel('Time')

        plot_filename = "%s_%s_%s.png" % (filename, label1, label2)
        _file = as_path(fs.dirname(_source_file), plot_filename)
        plt.savefig(_file)
        plt.cla()
