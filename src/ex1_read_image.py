#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that determines the transformation matrix from
the header of a block of a fits file
"""

import sys
import matplotlib.pyplot as plt
import mylib

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and display the associated picture
    """

    # Get pixels and header from a fits file
    pixels, header = mylib.get_pixels("../data/specific.fits")

    # Display the picture
    _, axis = plt.subplots()
    axis.imshow(pixels)
    plt.show()

    # Write the informations of the transformation matrix on ex1.txt file
    results = 'cd1_1: %.10f, cd1_2: %.10f, cd2_1: %.10f, cd2_2: %.10f' % \
             (header['CD1_1'], header['CD1_2'], \
              header['CD2_1'], header['CD2_2'])
    with open("ex1.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
