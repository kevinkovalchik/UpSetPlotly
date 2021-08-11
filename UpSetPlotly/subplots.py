import plotly.graph_objs as go
import plotly.subplots
from typing import List, Dict, Tuple, Iterable


def master_figure() -> go.Figure:
    """
    Return a plotly.graph_objs.Figure with 2x2 subplots.
    :return:
    """
    fig = plotly.subplots.make_subplots(2, 1, True, True, vertical_spacing=0.03)
    fig.update_xaxes(ticks='', row=2, col=1, tickvals=[], ticktext=[])
    return fig


def add_intersect_bar_subplot(fig: go.Figure, intersects: List[Dict]):
    """
    Add the intersect bar chart to the master figure (i.e. a figure with 2x2 subplots).
    :param fig: The plotly.graph_object.Figure object to add the subplot to
    :param intersects: The list of intersects, a list of dictionaries.
    :return:
    """
    numbers = [x['n'] for x in intersects]
    labels = [' & '.join(x['samples']) for x in intersects]
    fig.add_trace(go.Bar(x=labels, y=numbers), row=1, col=1)


def get_row_locations(n: int) -> List[Tuple[float, float]]:
    """
    Get the upper and lower range of each sample row for the table.
    :param n: The number of samples
    :return:
    """
    width = 1 / n
    bins = [(width * x, width * (x + 1)) for x in range(n)]
    bins.reverse()
    return bins


def add_rows_to_sample_table(fig: go.Figure, names: List[str]):
    row_colors = ['#ebf0f8', '#ced2d9']
    bins = get_row_locations(len(names))
    # add the alternating rows
    for i in range(len(names)):
        fig.add_shape(dict(type='rect', x0=0, x1=1, y0=bins[i][0], y1=bins[i][1],
                           line_width=0, fillcolor=row_colors[i % 2]),
                      row=2, col=1)
    # add white lines between them
    for i in range(0, len(bins) - 1):
        fig.add_shape(dict(type='line', x0=0, x1=1, y0=bins[i][0], y1=bins[i][0],
                           line=dict(width=1, color='white')),
                      row=2, col=1)
    fig.update_xaxes(range=[0, 1], row=2, col=1)
    fig.update_yaxes(range=[0, 1], row=2, col=1)
    # add y-axis tick labels
    tick_text = names
    tick_values = [(x[0] + x[1]) / 2 for x in bins]
    fig.update_yaxes(tickmode='array', tickvals=tick_values, ticktext=tick_text, row=2, col=1)


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
    x0 = x_center - 0.5 * width
    x1 = x_center + 0.5 * width
    y0 = y_center - 0.5 * height
    y1 = y_center + 0.5 * height
    shape = dict(type='circle', x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=color, line=dict(color='#2b306e', width=1))

    return shape


def add_intersect_symbols(fig: go.Figure, intersects: List[dict], names: List[str]):
    """

    :param fig:
    :param intersects:
    :param names:
    :return:
    """

    # we need to define how big the circles are. let's go with 2/3 of the row height to start
    n_samples = len(names)
    height = 1 / n_samples * 0.66
    n_intersects = len(intersects)
    width = 1 / n_intersects * 0.66

    # make a dictionary to define the location of samples
    row_bins = get_row_locations(n_samples)
    tick_values = [(x[0] + x[1]) / 2 for x in row_bins]
    sample_location = {name: loc for name, loc in zip(names, tick_values)}

    # make a list to iterate through that has the columns locations
    col_bins = get_row_locations(n_intersects)
    col_centers = [(x[0] + x[1]) / 2 for x in col_bins]

    # now we iterate through the intersects and add the circles and bars to the figure
    shapes = []
    for i in range(n_intersects):
        samples = intersects[i]['samples']
        x_center = col_centers[i]  # center of the intesect location
        y_locs = [sample_location[sample] for sample in samples]  # location of samples in this intersect

        # add bars
        min_y = min(y_locs)
        max_y = max(y_locs)
        fig.add_shape(vbar_shape(x_center=x_center,
                                 y0=min_y,
                                 y1=max_y,
                                 width=width*0.5),
                      row=2, col=1)

        # add circles
        for y_loc in y_locs:
            fig.add_shape(circle_shape(x_center=x_center,
                                       y_center=y_loc,
                                       width=width,
                                       height=height),
                          row=2, col=1)
