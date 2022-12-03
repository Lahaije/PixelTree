from math import cos, sin, tan, degrees, pi
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from typing import Union, List

from config import storage
from model.snap import RawSnapData


def plot_circle(ax: plt.Axes, radius=1):
    angle = np.linspace(0, 2 * np.pi, 150)

    x = radius * np.cos(angle)
    y = radius * np.sin(angle)

    ax.plot(x, y)
    ax.set_aspect(1)


def plot_point(ax: plt.Axes, x: Union[float, List[float]], y: Union[float, List[float]], color, size=20):
    ax.scatter(x, y, s=size, marker='*', edgecolors=color)


def plot_led_lines(ax: plt.Axes, snap: RawSnapData, phi: float, color):
    rot = [[cos(phi), -sin(phi)], [sin(phi), cos(phi)]]

    cam = snap.camera_distance()
    campos = np.dot([0, -cam], rot)

    plot_point(ax, campos[0], campos[1], color)

    for led in snap.snapl.values():
        if not led.reliable:
            continue

        angle = snap.angle_y(led)

        x = np.linspace(-5, 5, 100)
        y = (sin(angle) * cam - x * cos(angle - phi)) / (sin(angle - phi))

        x1 = []
        y1 = []
        for i in range(len(y)):
            if -4.5 < y[i] < 4.5:
                x1.append(x[i])
                y1.append(y[i])

        plt.plot(x1, y1, color='green', linewidth=0.1)

        x = [0, (1+cam) * tan(angle)]
        y = [-cam, 1]
        m1 = np.dot([x[0], y[0]], rot)
        m2 = np.dot([x[1], y[1]], rot)
        x1 = [m1[0], m2[0]]
        y1 = [m1[1], m2[1]]

        plt.plot(x1, y1, color=color, linewidth=0.1)
        plt.text(x1[1], y1[1], led.id, fontsize=4, color='black')


def plot_angle_estimates():
    snap = {'f0': RawSnapData(storage / 'fiets_0_white'),
            'f45': RawSnapData(storage / 'fiets_45'),
            'f90': RawSnapData(storage / 'fiets_90_white'),
            'f240': RawSnapData(storage / 'fiets_240_white'),
            'f270': RawSnapData(storage / 'fiets_270_white_floor')}

    matplotlib.rcParams["figure.dpi"] = 300
    figure, axes = plt.subplots(2, 2)

    for data in ((0, 0, 'f45'), (0, 1, 'f90'), (1, 0, 'f240'), (1, 1, 'f270')):
        estimate = snap['f45'].estimate_angle(snap[data[2]])
        line = snap['f45'].angle_fit_data(snap[data[2]])
        a, b = line.T

        axes[data[0], data[1]].set_title(f'Angle = {data[2][1:]} ->{int(degrees(estimate[0]))} {int(degrees(estimate[1]))}')
        axes[data[0], data[1]].plot(a, b, color='blue', linewidth=1)

    figure.subplots_adjust(hspace=.3)
    plt.show()


if __name__ == "__main__":
    block = {'f0': RawSnapData(storage / 'fiets_0_white'),
             'f45': RawSnapData(storage / 'fiets_45'),
             'f90': RawSnapData(storage / 'fiets_90_white'),
             'f240': RawSnapData(storage / 'fiets_240_white'),
             'f240_b': RawSnapData(storage / 'fiets_240_blue_1'),
             'f270': RawSnapData(storage / 'fiets_270_white_floor')}

    matplotlib.rcParams["figure.dpi"] = 300
    fig, im = plt.subplots()
    plot_circle(im)
    plot_led_lines(im, block['f0'], 0, 'red')
    plot_led_lines(im, block['f45'], pi/4, 'blue')
    fig.show()
