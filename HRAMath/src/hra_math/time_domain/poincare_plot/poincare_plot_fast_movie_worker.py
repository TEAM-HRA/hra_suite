'''
Created on Aug 21, 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    from enable.base import str_to_font
    from traits.trait_types import Callable
    from chaco.api import PlotGraphicsContext
    from chaco.api import ArrayPlotData
    from chaco.api import Plot
    from chaco.api import ColormappedScatterPlot
    from chaco.api import LinearMapper
    from chaco.api import ArrayDataSource
    from chaco.label_axis import LabelAxis
    from chaco.scatterplot import render_markers
    from kiva.constants import CIRCLE_MARKER as CIRCLE
    from hra_core.datetime_utils import get_time_label_for_miliseconds
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotFastMovieMakerWorker(object):
    """
    special fast movie generation class which uses chaco library
    """
    def __init__(self, pp_specs_manager):
        self.manager = pp_specs_manager
        self.pp_specs = self.manager.getMiniPoincarePlotSpecs()
        if len(self.pp_specs) == 0:
            return
        self.gc = None
        self.p0 = self.pp_specs[0]

        #set up specific values for fonts sizes based on products of a movie
        #height and arbitrary constants to give looking good picture
        self.axis_font = 'modern ' + str(self.manager.movie_height / 53)
        self.title_font = 'modern ' + str(self.manager.movie_height / 40)
        self.text_font = 'modern ' + str(self.manager.movie_height / 61)

    def initiate(self):
        if len(self.pp_specs) == 0:
            return False

        # only positive values are accepted
        x = self.p0.x_data[pl.where(self.p0.x_data > 0)]
        y = self.p0.y_data[pl.where(self.p0.y_data > 0)]

        x_min = pl.amin(x)
        x_max = pl.amax(x)
        y_min = pl.amin(y)
        y_max = pl.amax(y)
        value_min = x_min if x_min < y_min else y_min
        value_max = x_max if x_max > y_max else y_max

        self.pd = ArrayPlotData()
        self.pd.set_data("index", x)
        self.pd.set_data("value", y)

        index_ds = ArrayDataSource(x)
        value_ds = ArrayDataSource(y)

        # Create the plot
        self._plot = Plot(self.pd)
        self._plot.index_range.add(index_ds)
        self._plot.value_range.add(value_ds)

        self._plot.index_mapper.stretch_data = False
        self._plot.value_mapper.stretch_data = False
        self._plot.value_range.set_bounds(value_min, value_max)
        self._plot.index_range.set_bounds(value_min, value_max)

        # Create the index and value mappers using the plot data ranges
        imapper = LinearMapper(range=self._plot.index_range)
        vmapper = LinearMapper(range=self._plot.value_range)

        # add axis labels
        bottom_axis = LabelAxis(self._plot, orientation='bottom',
                               title='RR(n) [ms]',
                               positions=range(1, 20),
                               title_font=self.axis_font)
        self._plot.underlays.append(bottom_axis)
        left_axis = LabelAxis(self._plot, orientation='left',
                               title='RR(n+1) [ms]',
                               positions=range(1, 20),
                               title_font=self.axis_font)
        self._plot.underlays.append(left_axis)

        color = "white"

        self.scatter = __PoincarePlotScatterPlot__(
                        self.p0,
                        self.manager,
                        index=index_ds,
                        value=value_ds,
                        #color_data=color_ds,
                        #color_mapper=color_mapper,
                        #fill_alpha=0.4,
                        color=color,
                        index_mapper=imapper,
                        value_mapper=vmapper,
                        marker='circle',
                        marker_size=self.manager.active_point_size,
                        line_width=0
                        #outline_color='white'
                        )
        self._plot.add(self.scatter)

        self._plot.plots['var_size_scatter'] = [self.scatter]

        # Tweak some of the plot properties
        self._plot.title = "Poincare plot"
        self._plot.title_font = self.title_font
        self._plot.line_width = 0.5
        self._plot.padding = 50

        self._plot.do_layout(force=True)
        self._plot.outer_bounds = [self.manager.movie_width,
                                   self.manager.movie_height]

        self.gc = PlotGraphicsContext(self._plot.outer_bounds,
                                      dpi=self.manager.movie_dpi)
        self.gc.render_component(self._plot)
        self.gc.set_line_width(0)

        self.gc.save(self.p0.frame_file)

        self.x_mean_old = None
        self.y_mean_old = None
        self._font = None

        self.tw = None
        self.th = None
        self.tx = None
        self.ty = None
        self.w = None
        self.h = None

        return True

    def plot(self, idx):
        if len(self.pp_specs) == 0:
            return
        p = self.pp_specs[idx]
        p_old = None if idx == 0 else self.pp_specs[idx - 1]

        if idx > 0:

            self.gc.set_line_width(0)

            if not p_old == None and not p_old.mean_plus == None:
                r_points = pl.array([[p_old.mean_plus, p_old.mean_minus]])
                r_points = self.scatter.map_screen(r_points)
                self.gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
                self.gc.draw_marker_at_points(r_points,
                                    self.manager.centroid_point_size, CIRCLE)

            __update_graphics_context__(self.gc, self.scatter, p, self.manager)

            r_points = pl.array([[p.mean_plus, p.mean_minus]])
            r_points = self.scatter.map_screen(r_points)
            self.gc.set_fill_color(self.manager.centroid_color_as_tuple)
            self.gc.draw_marker_at_points(r_points,
                                    self.manager.centroid_point_size, CIRCLE)
            #self.gc.save_state()

        self._draw_time_text(self.gc, p)
        self.gc.save_state()
        self.gc.save(p.frame_file)

    def _draw_time_text(self, gc, pp_spec):
        if pp_spec.level == 0:
            text = get_time_label_for_miliseconds(0)
        else:
            text = get_time_label_for_miliseconds(pp_spec.cum_inactive)

        if not self._font:
            self._font = str_to_font(None, None, self.text_font)

        gc.set_font(self._font)

        if not self.tw:
            _, _, self.tw, self.th = gc.get_text_extent(text)

            w_shift = self._plot.outer_bounds[0] - self._plot.width \
                        + self._plot.padding_right
            # divided by 2 because time label will be put at a title level
            # this means horizontal distance could be shorter
            h_shift = (self._plot.outer_bounds[1] - self._plot.height \
                        + self._plot.padding_top) / 2

            self.x = self._plot.outer_bounds[0] - self.tw - w_shift
            self.y = self._plot.outer_bounds[1] - self.th - h_shift
            self.w = self.tw + 2
            self.h = self.th + 2
            self.tx = self.x + self.w / 2.0 - self.tw / 2.0
            self.ty = self.y + self.h / 2.0 - self.th / 2.0

        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.rect(self.x, self.y, self.w, self.h)
        gc.draw_path()
        gc.set_fill_color((0.0, 0.0, 0.0, 1.0))
        gc.show_text_at_point(text, self.tx, self.ty)

        return


class __PoincarePlotScatterPlot__(ColormappedScatterPlot):

    # The function which actually renders the markers
    render_markers_func = Callable(render_markers)

    def __init__(self, pp_spec, pp_manager, **traits):
        """ Initializes the object.
        """
        ColormappedScatterPlot.__init__(self, **traits)
        self.__counter__ = 0
        self.__pp_spec__ = pp_spec
        self.__pp_manager__ = pp_manager

    def _render(self, gc, points):
        p0 = self.__pp_spec__  # alias

        gc.set_line_width(0)
        first = True
        #to get drawn the starting frame as correctly as possible,
        #all previous frames from the last MiniPoincarePlotSpecManager
        #are reconstructed
        for pp_spec_minimum in \
            self.__pp_manager__.getPreviousPoincarePlotSpecsMinimum():
            setattr(pp_spec_minimum, 'x_data', p0.x_data)
            setattr(pp_spec_minimum, 'y_data', p0.y_data)
            __update_graphics_context__(gc, self, pp_spec_minimum,
                                        self.__pp_manager__, first)
            first = False
        __update_graphics_context__(gc, self, p0, self.__pp_manager__,
                                    first=first)

        r_points = pl.array([[p0.mean_plus, p0.mean_minus]])
        r_points = self.map_screen(r_points)
        gc.set_fill_color(self.__pp_manager__.centroid_color_as_tuple)
        gc.draw_marker_at_points(r_points,
                            self.__pp_manager__.centroid_point_size, CIRCLE)
        gc.save_state()

        self.__counter__ = self.__counter__ + 1


def __update_graphics_context__(gc, scatter, pp_spec, manager, first=False):
    """
    function update graphics context of scatter plot based in
    information included in poincare plot specification object
    """
    p = pp_spec  # alias
    m = manager  # alias

    if first and p.level >= 0 and p.inactive_stop >= 0 and p.active_stop >= 0:
        r_points = pl.dstack(
            (p.x_data[p.inactive_stop:p.active_stop],
             p.y_data[p.inactive_stop:p.active_stop]))[0]
        r_points = scatter.map_screen(r_points)
        gc.set_fill_color(m.active_color_as_tuple)
        gc.draw_marker_at_points(r_points, m.active_point_size, CIRCLE)

    if p.inactive_start_2 >= 0 and p.inactive_stop_2 >= 0:
        r_points = pl.dstack(
                (p.x_data[p.inactive_start_2: p.inactive_stop_2],
                 p.y_data[p.inactive_start_2: p.inactive_stop_2]))[0]
        r_points = scatter.map_screen(r_points)
        gc.set_fill_color(m.inactive_color_as_tuple)
        gc.draw_marker_at_points(r_points, m.inactive_point_size, CIRCLE)

    if first and p.level >= 0 and p.inactive_stop >= 0:
        r_points = pl.dstack(
                (p.x_data[: p.inactive_stop],
                 p.y_data[: p.inactive_stop]))[0]
        r_points = scatter.map_screen(r_points)
        gc.set_fill_color(m.inactive_color_as_tuple)
        gc.draw_marker_at_points(r_points, m.inactive_point_size, CIRCLE)
    elif p.inactive_start >= 0 and p.inactive_stop >= 0:
        r_points = pl.dstack(
                    (p.x_data[p.inactive_start: p.inactive_stop],
                     p.y_data[p.inactive_start: p.inactive_stop]))[0]
        r_points = scatter.map_screen(r_points)
        gc.set_fill_color(m.inactive_color_as_tuple)
        gc.draw_marker_at_points(r_points, m.inactive_point_size, CIRCLE)

    if (not first or p.level == 0) \
        and p.active_start >= 0 and p.active_stop >= 0:
        r_points = pl.dstack(
                (p.x_data[p.active_start: p.active_stop],
                 p.y_data[p.active_start: p.active_stop]))[0]
        r_points = scatter.map_screen(r_points)
        gc.set_fill_color(m.active_color_as_tuple)
        gc.draw_marker_at_points(r_points, m.active_point_size, CIRCLE)
