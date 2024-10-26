import numpy as np
import matplotlib.pyplot as plt


def plot_circle(x, y, radius, angle_start, angle_end, color):
    angle = np.linspace(angle_start * np.pi, angle_end * np.pi, int((angle_end - angle_start) * 75))

    radius = radius
    i = radius * np.cos(angle) + x
    j = radius * np.sin(angle) + y

    axes.plot(i, j, color=color)


def plot_point(x, y, name, color='black'):
    axes.scatter(x, y, 50, color=color)
    axes.text(x, y, f' {name}', fontsize=12, color='black')


figure, axes = plt.subplots(1)

# Camera
axes.text(0, -2, ' C1', fontsize=12, color='red')
axes.scatter(0, -2, 250, color='black', marker='*')
axes.text(-1.5, 1.5, ' C2', fontsize=12, color='red')
axes.scatter(-1.5, 1.5, 250, color='black', marker='*')

axes.plot([0, 0], [0, -2], color='black')
axes.plot([-.75, 0], [-.5, -2], color='black')
axes.plot([.7, 0], [.2, -2], color='black')


axes.plot([0, -1.5], [0, 1.5], color='black')
axes.plot([-.75, -1.5], [-.5, 1.5], color='black')
axes.plot([.7, -1.5], [.2, 1.5], color='black')

axes.text(-.35, -.2, 'Θ', fontsize=12, color='black')
axes.scatter(0, 0, 500, color='red', marker='+')


plot_circle(0, 0, 1, 0, 2, 'blue')
plot_circle(0, 0, .2, .75, 1.5, 'black')
plot_circle(0, -2, .4, .4, .65, 'red')
axes.text(-.25, -1.5, 'α1', fontsize=10, color='red')
axes.text(0, -1.5, 'α2', fontsize=10, color='red')

plot_circle(-1.5, 1.5, .4, 1.63, 1.83, 'red')
axes.text(-1.3, 1, 'β1', fontsize=10, color='red')
axes.text(-1.05, 1.05, 'β2', fontsize=10, color='red')

plot_point(-.75, -.5, 'P1')
plot_point(.7, .2, 'P2')

axes.set_aspect(1)

plt.title('Camera angles')

plt.show()
