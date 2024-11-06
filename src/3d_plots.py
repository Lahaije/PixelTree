from typing import List

from dash import Dash, dcc, html
import plotly.express as px
import plotly.graph_objects as go

from math import cos, pi, sin
import pandas as pd

from config import NUM_PIXELS
from height import HEIGHT
from width import WIDTH


class Plot:
    def __init__(self):
        self.df = pd.DataFrame(columns=['lid', 'X', 'Y', 'Z', 'name'])
        self.reeksen: List[List[int]] = []

    def add_reeks(self, leds: List[int]):
        """
        Add a reeks of leds who are in a strait vertical line.
        The list should contain the LED id's
        """
        self.reeksen.append(leds)

    def add_point(self, lid, x, y, z, name):
        self.df = pd.concat([pd.DataFrame([[lid, x, y, z, name]], columns=self.df.columns), self.df], ignore_index=True)

    def show(self, text=False):
        if text:
            fig = px.scatter_3d(self.df, x='X', y='Y', z='Z', color="name", text="lid")
        else:
            fig = px.scatter_3d(self.df, x='X', y='Y', z='Z', color="name", width=10)

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0)
        )

        traces = []

        for reeks in self.reeksen:
            traces.append(px.line_3d(self.df.loc[[599-e for e in reeks]], 'X', 'Y', 'Z'))
            traces[-1].update_traces(line=dict(color='rgba(0,0,0,1)', width=5))

        data = fig.data
        for trace in traces:
            data = data + trace.data

        figure = go.Figure(data=data)

        app = Dash()
        app.layout = html.Div(
            [dcc.Graph(figure=figure, style={'height': '90vh'})],
            style={'width': '100%', 'display': 'inline-block', 'height': '100%'}
        )

        app.run_server(debug=True, use_reloader=False)


def x(r: float, theta: float) -> float:
    return r * cos(theta)


def y(r: float, theta: float) -> float:
    return r * sin(theta)


def theta(i: int) -> float:
    """
    Return a variable theta depending on how many leds are needed to complete a circle at the given height.
    """
    mapping = [57, 142, 218, 296, 365, 424, 470, 490, 523, 549, 563, 590]

    if i < mapping[0]:
        return 2*pi / (mapping[1] - mapping[0])

    try:
        for index in range(len(mapping)):
            if mapping[index] > i:
                return 2 * pi / (mapping[index] - mapping[index-1])
    except IndexError:
        pass
    return 2*pi / (mapping[-1] + mapping[-2])


def plot_model():
    plot = Plot()
    t = -4.287
    for i in range(NUM_PIXELS):
        t += theta(i)
        plot.add_point(i, x(WIDTH[i], -t), y(WIDTH[i], -t), HEIGHT[i], 'tree')

    # plot.add_reeks([74, 159, 234, 315, 380, 435, 512])
    plot.add_reeks([57, 142, 218, 296, 365, 424, 470, 490, 523, 549, 563, 590])
    plot.show(True)


if __name__ == "__main__":
    plot_model()

