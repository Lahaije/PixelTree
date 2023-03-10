from math import cos, sin, tan, degrees
from typing import Union, List

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from caculations import estimate_angle, angle_fit_data
from config import storage

from model.snap import RawSnapData


def old_plot():
    matplotlib.rcParams["figure.dpi"] = 300
    fig, im = plt.subplots()
    plot_circle(im)
    plot_led_lines(im, RawSnapData(storage / 'fiets_0_white') , 0, 'red')
    fig.show()


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

    cam = snap.camera_pos
    campos = np.dot([cam.x, cam.y], rot)

    plot_point(ax, campos[0], campos[1], color)

    for led in snap.snapl.values():
        if not led.reliable:
            continue

        angle = snap.pixel_phi(led)
        print(angle)
        x = np.linspace(-5, 5, 100)
        y = (sin(angle) * cam.distance - x * cos(angle - phi)) / (sin(angle - phi))

        x1 = []
        y1 = []
        for i in range(len(y)):
            if -4.5 < y[i] < 4.5:
                x1.append(x[i])
                y1.append(y[i])

        plt.plot(x1, y1, color='green', linewidth=0.1)

        x = [0, (1+cam.distance) * tan(angle)]
        y = [-cam.distance, 1]
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

    plot_angle_estimate(axes[0, 0], snap['f0'], snap['f45'])
    plot_angle_estimate(axes[0, 1], snap['f0'], snap['f90'])
    plot_angle_estimate(axes[1, 0], snap['f0'], snap['f240'])
    plot_angle_estimate(axes[1, 1], snap['f0'], snap['f270'])

    figure.subplots_adjust(hspace=.3)
    plt.show()


def plot_angle_estimate(ax: plt.Axes, cam1:RawSnapData, cam2:RawSnapData):
    estimate = estimate_angle(cam1, cam2)
    fit = angle_fit_data(cam1, cam2)
    a, b = fit.T

    ax.set_title(f'Angle {cam1.name} , {cam2.name} -> {int(degrees(estimate[0]))} {int(degrees(estimate[1]))}')
    ax.plot(a, b, color='blue', linewidth=1)


if __name__ == "__main__":
    plot_angle_estimates()
