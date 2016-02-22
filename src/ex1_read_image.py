#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that determines the transformation matrix
of a block of a fits file
"""

import sys

import matplotlib.pyplot as plt
from astropy.io import fits


def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and display the associated picture
    """

    # Create empty variables to prevent exception when opening the file
    pixels = None
    header = None

    # Open the fits file specific.fits and put data in pixels variable
    with fits.open("../data/specific.fits") as fits_data:
        pixels = fits_data[0].data
        header = fits_data[0].header

    # Display the picture
    _, main_axes = plt.subplots()
    main_axes.imshow(pixels)
    plt.show()

    # Write the informations of the transformation matrix on ex1.txt file
    results = 'cd1_1: %.10f, cd1_2: %.10f, cd2_1: %.10f, cd2_2: %.10f' % \
             (header['CD1_1'], header['CD1_2'], header['CD2_1'], header['CD2_2'])
    with open("ex1.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
