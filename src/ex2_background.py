#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which substract the background from the picure,
corresponding to the data contained in pixels
"""

import sys
import matplotlib.pyplot as plt
import mylib

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and display the associated picture without background
    """

    # Get pixels and header from a fits file
    pixels, _ = mylib.get_pixels("../data/specific.fits")

    # Process to the fit of the background
    x_array, y_array, maxvalue, background, dispersion = \
        mylib.modelling_parameters(pixels)

    # Remove the background
    filtered_pixels = mylib.remove_background(pixels, background, dispersion)

    # Plot both histograms and picture without background
    _, axis = plt.subplots(1, 2)

    # Plot histogram of data luminosity and result of the fit
    axis[0].plot(x_array, y_array, 'b+:', label='data')
    axis[0].plot(x_array, mylib.modelling_function( \
             x_array, maxvalue, background, dispersion), \
             'r.:', label='fit')
    axis[0].legend()
    axis[0].set_title('Flux distribution')
    axis[0].set_xlabel('Amplitude')
    axis[0].set_ylabel('Frequency')

    # Display the picture without the background
    axis[1].imshow(filtered_pixels)
    axis[1].set_title('Picture without background')
    plt.show()

    # Write informations about background and dispersion on ex2.txt file
    results = 'background: %i, dispersion: %i' % (background, dispersion)
    with open("ex2.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
