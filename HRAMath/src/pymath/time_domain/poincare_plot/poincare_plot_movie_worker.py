'''
Created on Aug 21, 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import gc
    import matplotlib.pyplot as plt
    import pylab as pl
    from matplotlib.patches import Rectangle
    from pycore.datetime_utils import get_time_label_for_miliseconds
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotMovieMakerWorker(object):
    """
    core functionality used to generate poincare plots
    """
    def __init__(self, pp_specs_manager):
        self.manager = pp_specs_manager
        self.pp_specs = self.manager.getMiniPoincarePlotSpecs()
        if len(self.pp_specs) == 0:
            return
        self.fig = plt.figure()

    def initiate(self):
        if len(self.pp_specs) == 0:
            return False
        self.ax = self.fig.add_subplot(1, 1, 1, adjustable='box', aspect=1.0)
        self.p0 = self.pp_specs[0]  # alias
        self.ax.axis(self.p0.range)
        self.ax.set_xlabel('$RR_{n}$ [ms]')
        self.ax.set_ylabel('$RR_{n+1}$ [ms]')

        empty_rectangle = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                                    edgecolor='none', linewidth=0)

        white = pl.array([255, 255, 255, 0]) / 255.0

        #x_data and y_data are the same for all items included in pp_specs
        #array, we have to add add one item for a centroid value
        x_data = pl.hstack((pl.copy(self.p0.x_data), pl.array([0])))
        y_data = pl.hstack((pl.copy(self.p0.y_data), pl.array([0])))

        colors0 = [white] * len(x_data)
        sizes0 = [self.p0.inactive_point_size] * len(x_data)

        #at the the last index is a centroid
        sizes0[-1] = self.p0.centroid_point_size
        colors0[-1] = self.p0.centroid_color

        if self.p0.level == 0:
            colors0[self.p0.active_start:self.p0.active_stop] = \
                    [self.p0.active_color] * (self.p0.active_stop
                                              - self.p0.active_start)
            sizes0[self.p0.active_start:self.p0.active_stop] = \
                    [self.p0.active_point_size] * (self.p0.active_stop
                                                   - self.p0.active_start)
        else:
            if self.p0.inactive_start >= 0 and self.p0.inactive_stop >= 0:
                colors0[:self.p0.inactive_stop] = \
                        [self.p0.inactive_color] * self.p0.inactive_stop
                sizes0[:self.p0.inactive_stop] = \
                        [self.p0.inactive_point_size] * self.p0.inactive_stop
            if self.p0.active_stop >= 0:
                colors0[self.p0.inactive_stop:self.p0.active_stop] = \
                    [self.p0.active_color] * (self.p0.active_stop
                                               - self.p0.inactive_stop)
                sizes0[self.p0.inactive_stop:self.p0.active_stop] = \
                    [self.p0.active_point_size] * (self.p0.active_stop
                                                    - self.p0.inactive_stop)
            if self.p0.inactive_start_2 >= 0 and self.p0.inactive_stop_2 >= 0:
                colors0[self.p0.inactive_start_2:self.p0.inactive_stop_2] = \
                   [self.p0.inactive_color] * (self.p0.inactive_stop_2
                                               - self.p0.inactive_start_2)
                sizes0[self.p0.inactive_start_2:self.p0.inactive_stop_2] = \
                   [self.p0.inactive_point_size] * (self.p0.inactive_stop_2
                                                - self.p0.inactive_start_2)

# for future use
#        if p.show_plot_legends == True:
#
#            if p.level == 0:
#                leg_plots = ax.legend((a_plot, c_plot),
#                                       ('biezacy PP', "controid"),
#                                       'upper right', scatterpoints=1)
#            else:
#                leg_plots = ax.legend((a_plot, i_plot, c_plot),
#                            ('biezacy PP', "poprzednie PP", "controid"),
#                            'upper right', scatterpoints=1)  # , shadow=True)
#            leg_plots.get_frame().set_alpha(0.5)
#            ltext = leg_plots.get_texts()
#            plt.setp(ltext, fontsize=8)

        self.scatter = self.ax.scatter(x_data, y_data, c=colors0, s=sizes0,
                     edgecolors='none', animated=False)

        if self.p0.level == 0:
            time_label = get_time_label_for_miliseconds(0)
        else:
            time_label = get_time_label_for_miliseconds(self.p0.cum_inactive)
        leg_time = self.ax.legend([empty_rectangle], [time_label],
                                  'upper left')
        leg_time.get_frame().set_alpha(0.5)
        ltext = leg_time.get_texts()
        plt.setp(ltext, fontsize=8)
        self.ax.add_artist(leg_time)
        self.legend_text = ltext[0]
        self.legend_text.set_text(('%s [%d]') % (time_label, self.p0.idx))

        self.offsets = self.scatter.get_offsets()
        centroid = pl.array([self.p0.mean_plus, self.p0.mean_minus])
        self.offsets[-1].put(pl.arange(0, 2), centroid)
        return True

    def plot(self, idx):
        p = self.pp_specs[idx]
        if idx > 0:
            if idx % 100 == 0:
                gc.collect()

            time_label = get_time_label_for_miliseconds(p.cum_inactive)
            self.legend_text.set_text(('%s [%d]') % (time_label, p.idx))

            colors = self.scatter._facecolors
            sizes = self.scatter._sizes

            if p.inactive_start >= 0 and p.inactive_stop >= 0:
                sizes[p.inactive_start:p.inactive_stop] = p.inactive_point_size
                colors[p.inactive_start:p.inactive_stop, :] = p.inactive_color

            if p.inactive_start_2 >= 0 and p.inactive_stop_2 >= 0:
                sizes[p.inactive_start_2:p.inactive_stop_2] = p.inactive_point_size # @IgnorePep8
                colors[p.inactive_start_2:p.inactive_stop_2, :] = p.inactive_color # @IgnorePep8

            if p.active_start >= 0 and p.active_stop >= 0:
                sizes[p.active_start:p.active_stop] = p.active_point_size
                colors[p.active_start:p.active_stop, :] = p.active_color

            self.offsets = self.scatter.get_offsets()
            centroid = pl.array([p.mean_plus, p.mean_minus])
            self.offsets[-1].put(pl.arange(0, 2), centroid)
