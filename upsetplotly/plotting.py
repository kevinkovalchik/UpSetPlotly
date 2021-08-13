import plotly.graph_objs as go
import plotly.subplots
from typing import List, Dict, Tuple, Iterable, Optional, Union
from upsetplotly.set_functions import get_all_intersections, order_sample_intersections


def get_rgb_tuple(color: str) -> Tuple[int]:
    if color.startswith('#'):
        color = color[1:]
        rgb_color = [int(c1 + c2, 16) for c1, c2 in zip(color[::2], color[1::2])]
    elif color.startswith('('):
        rgb_color = [int(x) for x in color.replace('(', '').replace(')', '').split(',')]
    else:
        raise ValueError(f'Unrecognized color format: {color}. Must be hex or rgb.')
    if len(rgb_color) == 4:
        rgb_color = rgb_color[:-1]
    rgb_color = tuple(rgb_color)
    return rgb_color


class UpSetPlotly:
    def __init__(self, samples: List[Iterable], sample_names: List[str] = None):

        if sample_names:
            if not len(samples) == len(sample_names):
                raise ValueError('the length of samples and sample_names must be equal.')
        else:
            # if there are no names provided, use sequential integers starting at 1
            sample_names = [str(x) for x in range(1, len(samples) + 1)]

        self.samples = [set(x) for x in samples]
        self.sample_names = sample_names
        self.sample_data = {sample: data for sample, data in zip(sample_names, samples)}
        self.intersections = get_all_intersections(self.samples, self.sample_names)
        self.intersections = [x for x in self.intersections if x['n'] > 0]  # drop any empty intersections
        self.n_plotted_intersections: int = 0
        self.all_elements = set()
        self.all_elements.update(*self.samples)
        self.n_rows = 2
        self.additional_data = []
        self.fig: go.Figure = None

    def add_secondary_plot(self, data: dict, label: str, plot_type: str = 'box') -> None:
        """
        Add data to generate a secondary plot above the bar chart. Can be called more than once to add multiple plots.
        :param data: A dictionary which maps values to elements found in the sample sets
        :param label: The label to use in the plot.
        :param plot_type:
        :return: None
        """
        if plot_type not in ['box', 'violin', 'swarm']:
            raise ValueError('plot_type must be one of {box, violin, swarm}')
        provided_elements = set(list(data.keys()))
        if len(self.all_elements - provided_elements) > 0:
            raise ValueError('There are elements in the provided samples which are missing in the secondary '
                             'data to plot. Check the data or, to ignore the missing data and plot anyway, '
                             'pass ignore_missing as True.')
        self.additional_data.append({'type': plot_type, 'data': data, 'label': label})
        self.n_rows += 1

    def plot(self, show_fig: bool = True, return_fig: bool = False,
             intersection_limit: str = None,
             order_by: str = None,
             color: str = None) -> Optional[go.Figure]:
        """
        Create the UpSetPlot.
        :param show_fig: Whether or not to show the figure.
        :param return_fig: Whether or not to return the Figure object.
        :param intersection_limit: A string indicating a limit on how small an intersection to plot. Must be of this
        form: "by_sample [a float between 0 and 1]" or "by_total [a float between 0 and 1]". For example, if you
        give "by_sample 0.05", then any intersection which is 5% or greater of any sample will be displayed. If you
        were to give "by_total 0.05", then any intersection which is 5% or greater of the total number of unique
        elements would be displayed.
        :param order_by: If the intersections should be ordered according to size. Must be one of
        {increasing, decreasing}
        :return:
        """
        if color is None:
            color = '#636efa'

        if order_by:
            if order_by not in ['increasing', 'decreasing']:
                raise ValueError('order_by must be one of {increasing, decreasing}')
            intersections = order_sample_intersections(self.intersections, by=order_by)
        else:
            intersections = self.intersections

        if intersection_limit:
            cutoff = float(intersection_limit.split(' ')[1])
            if intersection_limit.startswith('by_total'):
                new_intersections = []
                total = len(self.all_elements)

                for intersect in intersections:
                    if intersect['n'] / total >= cutoff:
                        new_intersections.append(intersect)
                intersections = new_intersections

            elif intersection_limit.startswith('by_sample'):
                new_intersections = []

                for intersect in intersections:
                    keep = False
                    for sample in intersect['samples']:
                        if intersect['n'] / len(self.sample_data[sample]) >= cutoff:
                            keep = True
                            break
                    if keep:
                        new_intersections.append(intersect)
                intersections = new_intersections
            else:
                raise ValueError('intersection_limit must start with "by_total" or "by_sample". See docstring for '
                                 'details.')

            if len(intersections) == 0:
                raise RuntimeError('After filtering by intersection size there is no data to plot. Refine the value '
                                   'of "intersection_limit".')

        rows = 2 + len(self.additional_data)
        barplot_row = rows - 1
        intersection_row = rows
        self.fig = master_figure(n_samples=len(self.sample_names),
                                 rows=rows)
        add_intersect_bar_subplot(self.fig, intersections, row=barplot_row, color=color)
        add_rows_to_sample_table(self.fig, self.sample_names, row=intersection_row)
        add_circles_and_bars(self.fig, intersections, self.sample_names, row=intersection_row, color=color)
        for i in range(len(self.additional_data)):
            data = self.additional_data[i]
            add_additional_plot(self.fig,
                                data=data['data'],
                                label=data['label'],
                                intersections=intersections,
                                plot_type=data['type'],
                                row=i+1,
                                color=color)
        self.n_plotted_intersections = len(intersections)
        if show_fig:
            self.fig.show()
        if return_fig:
            return self.fig


def master_figure(n_samples: int, rows: int = 2) -> go.Figure:
    """
    Return a plotly.graph_objs.Figure with 2 subplots (2 rows, 1 column).
    :param n_samples: The number of samples involved.
    :param rows: The number of subplot rows to create.
    :return:
    """
    row_heights = []
    row_heights += [2.5] * (rows - 2)
    row_heights.append(10)
    row_heights.append(1 * n_samples)
    row_heights = [x/len(row_heights) for x in row_heights]
    fig = plotly.subplots.make_subplots(rows, 1, True, True, vertical_spacing=0.015,
                                        row_heights=row_heights)
    fig.update_xaxes(ticks='', row=rows, col=1, tickvals=[], ticktext=[])
    fig.update_yaxes(title_text='Intersection Size', row=rows-1, col=1)
    fig.update_layout(showlegend=False)

    for row in range(1, rows+1):
        fig.update_xaxes(fixedrange=True, col=1, row=row)
    fig.update_yaxes(fixedrange=True, col=1, row=rows)

    return fig


def add_intersect_bar_subplot(fig: go.Figure, intersections: List[Dict], row: int = 1, col: int = 1,
                              color: str = '#636efa'):
    """
    Add the intersect bar chart to the master figure (i.e. a figure with 2x2 subplots).
    :param fig: The plotly.graph_object.Figure object to add the subplot to
    :param intersections: The list of intersections, a list of dictionaries.
    :param row: The row of the subplot to be added.
    :param col: The column of the subplot to be added.
    :param color: Color of the bars
    :return:
    """
    numbers = [x['n'] for x in intersections]
    labels = [' & '.join(x['samples']) for x in intersections]
    fig.add_trace(go.Bar(x=labels, y=numbers, marker=dict(color=color)), row=row, col=col)


def get_row_locations(n: int) -> List[Tuple[float, float]]:
    """
    Get the upper and lower range of each sample row for the table.
    :param n: The number of samples
    :return:
    """
    width = 1 / n
    bins = [(1 - width * x, 1 - width * (x + 1)) for x in range(n)]  # subtract from one in there so they are descending
    return bins


def get_bar_locations(n: int) -> List[Tuple[float, float]]:
    """
    Get the upper and lower range of each sample row for the table.
    :param n: The number of samples
    :return:
    """
    width = 1 / n
    bins = [(width * x, width * (x + 1)) for x in range(n)]
    return bins


def add_rows_to_sample_table(fig: go.Figure, names: List[str], row: int = 2, col: int = 1):
    """
    Add striped rows and sample names to the "table" part of the figure.
    :param fig: The figure to modify. Must have 2 rows and one column.
    :param names: The list of sample names.
    :param row: The row of the subplot to be modified.
    :param col: The column of the subplot to be modified.
    :return:
    """
    row_colors = ['#ebf0f8', '#ced2d9']
    bins = get_row_locations(len(names))
    # add the alternating rows
    for i in range(len(names)):
        fig.add_shape(dict(type='rect', x0=0, x1=1, y0=bins[i][0], y1=bins[i][1],
                           line_width=0, fillcolor=row_colors[i % 2]),
                      row=row, col=col)
    # add white lines between them
    for i in range(0, len(bins) - 1):
        fig.add_shape(dict(type='line', x0=0, x1=1, y0=bins[i][0], y1=bins[i][0],
                           line=dict(width=1, color='white')),
                      row=row, col=col)
    fig.update_xaxes(range=[0, 1], row=row, col=col)
    fig.update_yaxes(range=[0, 1], row=row, col=col)
    # add y-axis tick labels
    tick_text = names
    tick_values = [(x[0] + x[1]) / 2 for x in bins]
    fig.update_yaxes(tickmode='array', tickvals=tick_values, ticktext=tick_text, row=row, col=col)


def vbar_shape(x_center: float, y0: float, y1: float, width: float, color: str = '#636efa') -> dict:
    """
    Create a vertical bar shape. Returns a dictionary which can be added to a plotly graph as a shape using
    Figure.update_layout(shapes=[...])
    :param x_center:
    :param y0:
    :param y1:
    :param width:
    :param color:
    :return:
    """
    color = get_rgb_tuple(color)
    color = f'rgb{color}'
    x0 = x_center - 0.5 * width
    x1 = x_center + 0.5 * width
    shape = dict(type='rect', x0=x0, x1=x1, y0=y0, y1=y1, line_color=color, fillcolor=color, opacity=0.6)

    return shape


def circle_shape(x_center: float, y_center: float, width: float, height: float, color: str = '#636efa'):
    """
    Create a circle shape. Returns a dictionary which can be added to a plotly graph as a shape using
    Figure.update_layout(shapes=[...])
    :param x_center:
    :param y_center:
    :param width:
    :param height:
    :param color:
    :return:
    """
    color = get_rgb_tuple(color)
    fillcolor = f'rgb{color}'
    linecolor = [x-50 if x-50 >= 0 else 0 for x in color]
    linecolor = f'rgb{tuple(linecolor)}'
    x0 = x_center - 0.5 * width
    x1 = x_center + 0.5 * width
    y0 = y_center - 0.5 * height
    y1 = y_center + 0.5 * height
    shape = dict(type='circle', x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=fillcolor, line=dict(color=linecolor, width=1))

    return shape


def add_circles_and_bars(fig: go.Figure, intersections: List[dict], names: List[str], row: int = 2, col: int = 1,
                         color:str = '#636efa'):
    """
    Add circles and bars indicating the samples to which a set belongs.
    :param fig: The figure being modified.
    :param intersections: The list of intersections (returned from get_all_intersects).
    :param names: The names of the samples.
    :param row: The row of the subplot to be modified.
    :param col: The column of the subplot to be modified.
    :return:
    """

    # we need to define how big the circles are. let's go with 2/3 of the row height to start
    n_samples = len(names)
    height = 1 / n_samples * 0.66
    n_intersects = len(intersections)
    width = 1 / n_intersects * 0.66

    # make a dictionary to define the location of samples
    row_bins = get_row_locations(n_samples)
    tick_values = [(x[0] + x[1]) / 2 for x in row_bins]
    sample_location = {name: loc for name, loc in zip(names, tick_values)}

    # make a list to iterate through that has the columns locations
    col_bins = get_bar_locations(n_intersects)
    col_centers = [(x[0] + x[1]) / 2 for x in col_bins]

    # now we iterate through the intersections and add the circles and bars to the figure
    shapes = []
    for i in range(n_intersects):
        samples = intersections[i]['samples']
        x_center = col_centers[i]  # center of the intersection location
        y_locs = [sample_location[sample] for sample in samples]  # location of samples in this intersect

        # add bars
        min_y = min(y_locs)
        max_y = max(y_locs)
        fig.add_shape(vbar_shape(x_center=x_center,
                                 y0=min_y,
                                 y1=max_y,
                                 width=width*0.5,
                                 color=color),
                      row=row, col=col)

        # add circles
        for y_loc in y_locs:
            fig.add_shape(circle_shape(x_center=x_center,
                                       y_center=y_loc,
                                       width=width,
                                       height=height,
                                       color=color),
                          row=row, col=col)


def add_additional_plot(fig: go.Figure, data: dict, label: str, intersections: List[Dict],
                        plot_type: str = 'box', row: int = 2, col: int = 1, color:str = '#636efa'):
    """
    Add an additional plot to the UpSetPlot.
    :param fig: The figure being modified.
    :param data: The data to be added. A dictionary of data values keyed by element.
    :param label: The label to be used for the y-axis.
    :param intersections: The intersection data in the UpSetPlot.
    :param plot_type: The type of plot to add. Must be one of {box, violin, swarm}.
    :param row: The row of the subplot to be modified.
    :param col: The column of the subplot to be modified.
    :return: None
    """
    if plot_type not in ['box', 'violin', 'swarm']:
        raise ValueError('plot_type must be one of {box, violin, swarm}')
    n_intersections = len(intersections)
    col_bins = get_bar_locations(n_intersections)
    col_centers = [(x[0] + x[1]) / 2 for x in col_bins]
    fig.update_yaxes(title_text=label, row=row, col=col)

    for i in range(n_intersections):
        intersection = intersections[i]
        x_loc = col_centers[i]
        data_to_plot = [data[x] for x in intersection['elements']]
        if plot_type == 'box':
            box_width = 1 / n_intersections * 0.8
            fig.add_trace(go.Box(x=[x_loc]*len(data_to_plot),
                                 y=data_to_plot,
                                 width=box_width,
                                 marker=dict(color=color),
                                 line=dict(color=color, width=1.5)
                                 ),
                          row=row, col=col)
        elif plot_type == 'violin':
            fig.add_trace(go.Violin(x=[x_loc]*len(data_to_plot),
                                    y=data_to_plot,
                                    #fillcolor=color,
                                    #opacity=0.6,
                                    marker=dict(color=color),
                                    line=dict(color=color, width=1.5)
                                    ),
                          row=row, col=col)
        else:
            fig.add_trace(go.Box(x=[x_loc]*len(data_to_plot),
                                 y=data_to_plot,
                                 fillcolor='rgba(255,255,255,0)',
                                 line={'color': 'rgba(255,255,255,0)'},
                                 marker={'color': color, 'size': 4},
                                 boxpoints='all',
                                 jitter=0.6,
                                 pointpos=0),
                          row=row, col=col)
