import numpy as np
import matplotlib.pyplot as plt


class XY_name:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


origin = XY_name(0, 0, 'origin')
c1 = XY_name(0, -2, 'C1')
c2 = XY_name(2, -1, 'C2')
l0 = XY_name(.6, -.7, 'L0')
l1 = XY_name(-.75, -.5, 'L1')
l2 = XY_name(.7, .2, 'L2')


def plot_circle(x, y, radius, angle_start, angle_end, color):
    angle = np.linspace(angle_start * np.pi, angle_end * np.pi, int((angle_end - angle_start) * 75))

    radius = radius
    i = radius * np.cos(angle) + x
    j = radius * np.sin(angle) + y

    axes.plot(i, j, color=color)


def plot_line(p1:XY_name, p2:XY_name, linestyle='solid', color='black'):
    axes.plot((p1.x, p2.x), (p1.y, p2.y), linestyle=linestyle, color=color)


def plot_point(p:XY_name, color='black'):
    axes.scatter(p.x, p.y, 50, color=color)
    axes.text(p.x, p.y, f' {p.name}', fontsize=12, color='black')


def plot_camera(c: XY_name):
    axes.text(c.x, c.y, f' {c.name}', fontsize=12, color='red')
    axes.scatter(c.x, c.y, 200, color='black', marker='*')
    plot_line(c, origin, linestyle='dashed', color='red')


figure, axes = plt.subplots(1)
axes.axis('equal')
plot_circle(0, 0, 1, 0, 2, 'blue')

plt.title('Camera angles')

# Camera
plot_camera(c1)
plot_camera(c2)

plot_point(l0)
plot_point(l1)
plot_point(l2)

plot_line(c1, l0, color='green')
plot_line(c2, l0, color='green')

axes.text(.03, -1.7, f'α', fontsize=12, color='black')
axes.text(1.3, -.83, f'β', fontsize=12, color='black')
axes.text(.1, -.3, f'θ', fontsize=12, color='black')

plt.show()