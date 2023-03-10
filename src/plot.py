from copy import deepcopy
from typing import Union
import numpy as np

import plotly
import plotly.graph_objects as go

from config import storage
from math import pi
from model.snap import RawSnapData
from model.positions import Pixel
from caculations import all_intersection
from model.transformations import rotation_matrix, rotate_xy


def plotly_circle(fig: go.Figure):
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=-1, y0=-1, x1=1, y1=1,
                  line_color="black"
                  )


def plotly_point(fig: go.Figure, x: float, y: float, color='red', name='', symbol='star'):
    """
    Plot a point at x, y
    """
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode="markers",
        marker=dict(color=color, symbol=symbol),
        name=name
    ))


def plotly_line(fig: go.Figure, p1: Union[Pixel, np.array], p2: Union[Pixel, np.array], color='red', name=''):
    """
    Plot a line from p1 to p2
    :return:
    """
    if isinstance(p1, Pixel):
        p1 = p1.coord
    if isinstance(p2, Pixel):
        p2 = p2.coord
    fig.add_trace(go.Scatter(
        x=[p1[0], p2[0]],
        y=[p1[1], p2[1]],
        mode='lines+markers',
        line=dict(color=color),
        name=name
))


def plotly_led_lines(fig: go.Figure, snap: RawSnapData, phi: float, color):
    """
    PLot a line for each reliable led in the x, y plane
    :param fig:
    :param snap:
    :param phi:
    :param color:
    :return:
    """
    cam = deepcopy(snap.camera_pos)
    campos = np.dot(cam.coord, rotation_matrix(phi))

    cam.coord = campos

    plotly_point(fig, campos[0], campos[1], color, cam.name)

    vector = rotate_xy(np.array([-2, 0, 0]), phi)  # Vector is used as endpoint for the line.
    for led in snap.snapl.values():
        if not led.reliable:
            continue

        angle = snap.pixel_phi(led)

        led_pos = np.dot(vector - cam.coord, rotation_matrix(angle)) + cam.coord

        plotly_line(fig, cam.coord, led_pos, color, led.id)


def plotly_intersection(fig, cam1: RawSnapData, cam2: RawSnapData, angle, color='black'):
    data = all_intersection(cam1, cam2, angle)
    for key, led in data.items():
        plotly_point(fig, led[0], led[1], color, key)


def plotly_pixel_data(fig, data):
    for key, led in data.items():
        nx = key + 1
        if nx in data:
            plotly_line(fig, led, data[nx], 'green')
        plotly_point(fig, led[0], led[1], 'black', key)


if __name__ == "__main__":
    block = {'f0': RawSnapData(storage / 'fiets_0_white'),
             'f45': RawSnapData(storage / 'fiets_45'),
             'f90': RawSnapData(storage / 'fiets_90_white'),
             'f240': RawSnapData(storage / 'fiets_240_white'),
             'f270': RawSnapData(storage / 'fiets_270_white_floor')}

    figure = go.Figure()
    plotly_circle(figure)

    test = pi / 100 * 40
    plotly_led_lines(figure, block['f90'], test, 'blue')
    plotly_led_lines(figure, block['f45'], pi / 4, 'green')
    plotly_led_lines(figure, block['f0'], 0, 'red')

    plotly_intersection(figure, block['f0'], block['f45'], pi / 3.5)
    plotly_intersection(figure, block['f0'], block['f90'], test)

    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    plotly.offline.plot(figure)



