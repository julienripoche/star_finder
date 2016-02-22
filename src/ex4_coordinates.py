#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math
import sys

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

import library
import mylib


def main():
    """ ex 4"""

    # Create empty variables to prevent exception when opening the file
    pixels = None

    # Open the fits file common.fits and put data in pixels variable
    with fits.open("../data/common.fits") as fits_data:
        pixels = fits_data[0].data
        header = fits_data[0].header

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

    # Instantiate conversion object
    my_wcs = library.WCS(header)

    # Compute WCS coordinates for the image corners
    #corner_pixel = [(0, 0), (0, n_row - 1), (n_column - 1, 0), (n_column - 1, n_row - 1)]
    #corner_celestial = [my_wcs.convert_to_radec(x, y) for x, y in corner_pixel]

    # Compute WCS coordinates for every cluster centroid
    for cluster in cluster_array:
        pixel_coords = cluster.centroid_pixel
        cluster.centroid_WCS = my_wcs.convert_to_radec(pixel_coords[0], pixel_coords[1])

    # remove the background
    above = pixels >= threshold
    filtered_pixels = above * (pixels - background)

    # Display the picture
    fig, axis = plt.subplots()
    axis.imshow(filtered_pixels)

    # Put all cluster celestial coordinates
    #for cluster in cluster_array:
    #    axis.text(cluster.centroid_pixel[0],  cluster.centroid_pixel[1], \
    #              'ra: %.10f, dec: %.10f' % \
    #              (cluster.centroid_WCS[0], cluster.centroid_WCS[1]), \
    #              fontsize=14, color='white')

    # Move definition
    def move(event):
        x_position = event.xdata
        y_position = event.ydata
        ra, dec = my_wcs.convert_to_radec(x_position, y_position)
        axis = event.inaxes
        text = axis.text(x_position, y_position, 'ra: %.6f, dec: %.6f' % (ra, dec), \
                  fontsize=14, color='white')
        event.canvas.draw()
        text.remove()

    # Use event handler
    fig.canvas.mpl_connect('motion_notify_event', move)
    plt.show()

    # Find the celestial coordinates of the main cluster
    greatest_integral = 0
    centroid_coords = None
    for cluster in cluster_array:
        if cluster.integrated_luminosity > greatest_integral:
            greatest_integral = cluster.integrated_luminosity
            centroid_coords = cluster.centroid_pixel
    main_cluster_ra, main_cluster_dec = \
        my_wcs.convert_to_radec(centroid_coords[0], centroid_coords[1])

    # Write the informations of the transformation matrix on ex4.txt file
    results = 'right ascension: %.3f, declination: %.3f' % \
             (main_cluster_ra, main_cluster_dec)
    with open("ex4.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
