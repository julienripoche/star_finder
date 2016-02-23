#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which substract the background from the image
"""

import sys

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from astropy.io import fits

import mylib


def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and display the associated picture, after the background has been removed
    """

    # Create empty variables to prevent exception when opening the file
    pixels = None

    # Open the fits file common.fits and put data in pixels variable
    with fits.open("../data/specific.fits") as fits_data:
        pixels = fits_data[0].data

    # Process the fit of the background
    x, y, maxvalue, background, dispersion = mylib.modelling_parameters(pixels)

    # remove the background
    filtered_pixels = mylib.remove_background(pixels, background, dispersion)

    # Display the picture without the background
    fig, axis = plt.subplots()
    plt.subplots_adjust(left = 0.1, bottom = 0.25)
    axis.imshow(filtered_pixels)
    axis.set_title('Picture without background')

    slider_axis = plt.axes([0.2, 0.1, 0.6, 0.105])
    threshold_min = max(0, background - 6.0 * dispersion)
    threshold_max = background + 10.0*dispersion
    threshold_init = background + 6.0*dispersion
    my_widget = widgets.Slider(slider_axis, 'threshold', threshold_min, threshold_max, valinit=threshold_init)

    # On_click definition
    def slider_action(threshold):
        axis.cla()
        filtered_pixels = mylib.remove_background(pixels, background, dispersion, threshold=threshold)
        axis.imshow(filtered_pixels)
        axis.set_title('Picture without background')
        fig.canvas.draw() # draw_idle()

    my_widget.on_changed(slider_action)
    plt.show()

    # Write the informations of the transformation matrix on ex2.txt file
    results = 'background: %i, dispersion: %i' % (background, dispersion)
    with open("ex2.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
