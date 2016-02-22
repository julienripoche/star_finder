#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which find cluster in the picture using recursive functions
"""

import math
import sys

import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

import mylib


def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and find cluster of pixels in which each pixel has a luminosity greater than
    a threshold (linked to the value of the background)
    """

    # Create empty variables to prevent exception when opening the file
    pixels = None

    # Open the fits file common.fits and put data in pixels variable
    with fits.open("../data/specific.fits") as fits_data:
        pixels = fits_data[0].data

    # Build a flat list of the pixel values
    pixels_flat = pixels.ravel()

    # build the pixel distribution
    bin_number = 200
    # pylint: disable=E
    bin_values, bin_boundaries = np.histogram(pixels_flat, bin_number)

    # normalize the distribution for the gaussian fit
    max_y = np.float(np.max(bin_values))
    normal_y = bin_values/max_y
    max_x = np.float(np.max(bin_boundaries))
    normal_x = bin_boundaries[:-1]/max_x

    # Fit the data with the gaussian modelling function and rescale the parameters
    fit, _ = curve_fit(mylib.modelling_function, normal_x, normal_y)
    background = fit[1] * max_x
    dispersion = math.fabs(fit[2] * max_x)

    # remove the background
    threshold = background + 6.0 * dispersion

    # Initiate some variables
    pixels_shape = pixels.shape
    marks = np.zeros(pixels_shape)
    n_row, n_column = pixels_shape
    cluster_array = []

    # Loop over the pixels and put the list of cluster in cluster_array
    for i in range(n_row):
        for j in range(n_column):
            if marks[i][j] != 1:
                marks[i][j] = 1
                if pixels[i][j] >= threshold:
                    cluster = mylib.Cluster(pixels, marks, threshold)
                    cluster.cluster_exploration(i, j)
                    marks = cluster.marks_updater()
                    cluster_array.append(cluster)

    # Find the number of clusters, the greatest integral and the associated centroid
    clusters_number = len(cluster_array)
    greatest_integral = 0
    centroid_coords = None
    for cluster in cluster_array:
        if cluster.integrated_luminosity > greatest_integral:
            greatest_integral = cluster.integrated_luminosity
            centroid_coords = cluster.centroid_pixel

    # Write the informations of the transformation matrix on ex3.txt file
    results = 'number of clusters: %2d, ' % (clusters_number) \
            + 'greatest integral: %7d, ' % (greatest_integral) \
            + 'centroid x: %4.1f, centroid y: %4.1f' % (centroid_coords[0], centroid_coords[1])
    with open("ex3.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
