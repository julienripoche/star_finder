#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Project 2:
Module which allows to change the threshold
with the use of a widget, and calculate
the number of clusters
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import mylib

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and display the associated picture without background,
    the threshold can be ajusted with a widget,
    calculate the number of clusters
    """

    # Get pixels and header from a fits file
    pixels, _ = mylib.get_pixels("../data/specific.fits")

    # Process to the fit of the background
    _, _, _, background, dispersion = mylib.modelling_parameters(pixels)

    # Remove the background
    filtered_pixels = mylib.remove_background(pixels, background, dispersion)

    # Display the picture without the background
    fig, axis = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.25)
    axis.imshow(filtered_pixels)
    axis.set_title('Picture without background')

    # Define the slider axis and the widget associated
    slider_axis = plt.axes([0.2, 0.1, 0.6, 0.105])
    threshold_min = background
    threshold_max = background + 30.0 * dispersion
    threshold_init = background + 6.0 * dispersion
    my_widget = widgets.Slider(slider_axis, 'threshold', threshold_min, \
                               threshold_max, valinit=threshold_init)

    # slider_action function definition
    def slider_action(threshold):
        """
        Function called when the threshold value is changed,
        the filtered_pixels array is recalculated
        and the canvas is redrawn
        """
        axis.cla() # delete the previous imshow
        filtered_pixels = mylib.remove_background(pixels, background, \
                          dispersion, threshold=threshold)
        axis.imshow(filtered_pixels)
        try: # if too many recursion, say that threshold is too low
            cluster_array = mylib.get_cluster_array(pixels, background, dispersion, threshold)
            axis.set_title('Picture without background : number of clusters = %s' % \
                      (len(cluster_array)))
        except RuntimeError:
            axis.set_title('Picture without background : threshold is too low')
        fig.canvas.draw() # redraw

    # Use event handler
    my_widget.on_changed(slider_action)
    plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
