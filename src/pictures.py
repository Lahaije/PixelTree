"""
This file contains the functions making plots of the data.
"""
from Boom.src.analyze_data import DataContainer, get_new_plot, optimize_led_strings, plot_leds_colored, \
    export_led_positions


def show_data(snap_name: str, scale, store=False):
    """
    :param snap_name: Name of the snap folder
    :param scale: scale
    :param store: If false, plot shows in window. If True, image is stored in snap folder.
    :return:
    """
    holding = DataContainer(snap_name)

    plot = get_new_plot(snap_name, scale, holding)

    """
    for string in holding.led_strings:
        string.fill_coord()
        for i in range(len(string.coord) - 1):
            plot.draw_line(string.coord[i], string.coord[i + 1], 'red')
    """

    optimize_led_strings(holding)

    for string in holding.led_strings:
        for i in range(len(string.coord) - 1):
            plot.draw_line(string.coord[i], string.coord[i + 1], 'yellow')
            # plot.line_mx_c(string.m, string.c, 'red')

    plot_leds_colored(plot, holding)

    if store:
        plot.store('show_data')
    else:
        plot.show()

    """
    data = {'m': holding.m, 'c': holding.c}
    for led in holding.data:
        data[led] = holding.data[led].coord

    export_led_positions(snap_name, data)
    """
