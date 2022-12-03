from math import cos, sin
import numpy as np
from pandas import concat
import plotly.express as px
import plotly
import plotly.graph_objects as go

from config import storage
from model.snap import RawSnapData
from model.triangulation import triangulate


def rotation_matrix(phi) -> np.array:
    return np.array([[cos(phi), -sin(phi), 0],
                     [sin(phi), cos(phi), 0],
                     [0, 0, 1]])


def plot_led_3d(led_dict, color, angle):
    x = []
    y = []
    z = []
    text = []
    col = []
    for key, value in led_dict.items():
        pos = np.inner(value, rotation_matrix(angle))
        text.append(key)
        x.append(pos[0])
        y.append(pos[1])
        z.append(pos[2])
        col.append(color)

    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers+text",
        name="Markers and Text",
        text=text,
        marker=dict(color=color),
        textposition="bottom center"
    ))


if __name__ == "__main__":
    block = {'f0': RawSnapData(storage / 'fiets_0_white'),
             'f45': RawSnapData(storage / 'fiets_45'),
             'f90': RawSnapData(storage / 'fiets_90_white'),
             'f240': RawSnapData(storage / 'fiets_240_white'),
             'f240_b': RawSnapData(storage / 'fiets_240_blue_1'),
             'f270': RawSnapData(storage / 'fiets_270_white_floor')}

    angles = triangulate(block['f0'], block['f45'], block['f240'])

    l1 = block['f0'].all_intersection(block['f45'], angles[0])
    l2 = block['f45'].all_intersection(block['f240'], angles[1])
    l3 = block['f0'].all_intersection(block['f240'], angles[2])

    df = concat([block['f0'].dataframe,
                 block['f45'].dataframe.dot(rotation_matrix(angles[0])),
                 block['f240'].dataframe.dot(rotation_matrix(angles[1]))
                 ])

    fig = px.scatter_3d(df, x=0, y=1, z=2)

    plot_led_3d(l1, 1, 0)
    plot_led_3d(l2, 2, 0)
    plot_led_3d(l3, 3, -angles[0])

    fig.update_layout(scene={'xaxis_title': 'X', 'yaxis_title': 'Y', 'zaxis_title': 'Z'})

    plotly.offline.plot(fig)



    exit()


    excluded = ('fiets_0_white_2', 'fiets_90_white_2', 'fiets_90_white_3', 'fiets_90_white_4')

