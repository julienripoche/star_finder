#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which substract the background from the image
"""

import sys

import matplotlib.pyplot as plt
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

    # Plot the data histogram and the result of the fit
    _, axis = plt.subplots()
    plt.plot(x, y, 'b+:', label='data')
    plt.plot(x, mylib.modelling_function(x, maxvalue, background, dispersion), 'r.:', label='fit')

    # put a title and name axis
    axis.legend()
    axis.set_title('Flux distribution')
    axis.set_xlabel('Amplitude')
    axis.set_ylabel('Frequency')
    plt.show()

    # Display the picture without the background
    _, axis = plt.subplots()
    axis.imshow(filtered_pixels)
    axis.set_title('Picture without background')
    plt.show()

    # Write the informations of the transformation matrix on ex2.txt file
    results = 'background: %i, dispersion: %i' % (background, dispersion)
    with open("ex2.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
