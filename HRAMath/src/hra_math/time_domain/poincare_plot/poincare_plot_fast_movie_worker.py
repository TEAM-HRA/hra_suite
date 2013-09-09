'''
Created on Aug 21, 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    from traits.trait_types import Callable
    from chaco.api import PlotGraphicsContext
    from chaco.api import ArrayPlotData
    from chaco.api import Plot
    from chaco.api import ColormappedScatterPlot
    from chaco.api import LinearMapper
    from chaco.api import ArrayDataSource
    from chaco.scatterplot import render_markers
    from kiva.constants import CIRCLE_MARKER
except ImportError as error:
    print_import_error(__name__, error)

_marker_size = 5


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
                        marker_size=_marker_size,
                        line_width=0
                        #outline_color='white'
                        ) #  marker_size)
        self._plot.add(self.scatter)

        self._plot.plots['var_size_scatter'] = [self.scatter]

        # Tweak some of the plot properties
        self._plot.title = "Poincare plot"
        self._plot.line_width = 0.5
        self._plot.padding = 50

        self._plot.do_layout(force=True)
        self._plot.outer_bounds = [800, 800]

        self.gc = PlotGraphicsContext(self._plot.outer_bounds, dpi=70)
        self.gc.render_component(self._plot)
        self.gc.set_line_width(0)

        self.gc.save(self.p0.frame_file)

        self.x_mean_old = None
        self.y_mean_old = None

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
                _color = (1.0, 1.0, 1.0, 1.0)  # white color
                self.gc.set_fill_color(_color)
                self.gc.draw_marker_at_points(r_points, _marker_size,
                                              CIRCLE_MARKER)

            __update_graphics_context__(self.gc, self.scatter, p)

            r_points = pl.array([[p.mean_plus, p.mean_minus]])
            r_points = self.scatter.map_screen(r_points)
            _color = (0.0, 1.0, 0.0, 1.0)  # green color
            self.gc.set_fill_color(_color)
            self.gc.draw_marker_at_points(r_points, _marker_size,
                                          CIRCLE_MARKER)
            self.gc.save_state()

        self.gc.save(p.frame_file)


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
#        manager = self.__pp_manager__
#        if not manager.previous_manager == None:
#          for pp_spec in manager.previous_manager.getMiniPoincarePlotSpecs():
#                __update_graphics_context__(gc, self, pp_spec, first)
#                first = False
        __update_graphics_context__(gc, self, p0, first=first)

        r_points = pl.array([[p0.mean_plus, p0.mean_minus]])
        r_points = self.map_screen(r_points)
        _color = (0.0, 1.0, 0.0, 1.0)  # green color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size,
                                          CIRCLE_MARKER)
        gc.save_state()

        self.__counter__ = self.__counter__ + 1


def __update_graphics_context__(gc, scatter, pp_spec, first=False):
    """
    function update graphics context of scatter plot based in
    information included in poincare plot specification object
    """
    p = pp_spec  # alias

    if first and p.level >= 0 and p.inactive_stop >= 0 and p.active_stop >= 0:
        r_points = pl.dstack(
            (p.x_data[p.inactive_stop:p.active_stop],
             p.y_data[p.inactive_stop:p.active_stop]))[0]
        r_points = scatter.map_screen(r_points)
        _color = (1.0, 0.0, 0.0, 1.0)  # red color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size, CIRCLE_MARKER)

    if p.inactive_start_2 >= 0 and p.inactive_stop_2 >= 0:
        r_points = pl.dstack(
                (p.x_data[p.inactive_start_2: p.inactive_stop_2],
                p.y_data[p.inactive_start_2: p.inactive_stop_2]))[0]
        r_points = scatter.map_screen(r_points)
        _color = (0.0, 0.0, 0.0, 1.0)  # black color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size, CIRCLE_MARKER)

    if first and p.level >= 0 and p.inactive_stop >= 0:
        r_points = pl.dstack(
                (p.x_data[: p.inactive_stop],
                 p.y_data[: p.inactive_stop]))[0]
        r_points = scatter.map_screen(r_points)
        _color = (0.0, 0.0, 0.0, 1.0)  # black color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size, CIRCLE_MARKER)
    elif p.inactive_start >= 0 and p.inactive_stop >= 0:
        r_points = pl.dstack(
                    (p.x_data[p.inactive_start: p.inactive_stop],
                     p.y_data[p.inactive_start: p.inactive_stop]))[0]
        r_points = scatter.map_screen(r_points)
        _color = (0.0, 0.0, 0.0, 1.0)  # black color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size, CIRCLE_MARKER)

    if (not first or p.level == 0) \
        and p.active_start >= 0 and p.active_stop >= 0:
        r_points = pl.dstack(
                (p.x_data[p.active_start: p.active_stop],
                 p.y_data[p.active_start: p.active_stop]))[0]
        r_points = scatter.map_screen(r_points)
        _color = (1.0, 0.0, 0.0, 1.0)  # red color
        gc.set_fill_color(_color)
        gc.draw_marker_at_points(r_points, _marker_size, CIRCLE_MARKER)
