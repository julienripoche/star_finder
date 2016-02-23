#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

import library
import mylib


def main():
    """ ex 5"""

    # Create empty variables to prevent exception when opening the file
    pixels = None

    # Open the fits file common.fits and put data in pixels variable
    with fits.open("../data/specific.fits") as fits_data:
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

    # Compute WCS coordinates for every cluster centroid
    # and star names
    for cluster in cluster_array:
        pixel_coords = cluster.centroid_pixel
        cluster.centroid_WCS = my_wcs.convert_to_radec(pixel_coords[0], pixel_coords[1])
        cluster.find_star_name()

    # remove the background
    above = pixels >= threshold
    filtered_pixels = above * (pixels - background)

    # Display the picture
    fig, axis = plt.subplots()
    axis.imshow(filtered_pixels)

    # Put all cluster star names
    #for cluster in cluster_array:
    #    axis.text(cluster.centroid_pixel[0],  cluster.centroid_pixel[1], \
    #              cluster.star_name, \
    #              fontsize=14, color='white')

    # Put bounding boxes
    for cluster in cluster_array:
        axis.add_patch(patches.Rectangle(cluster.bounding_box[0], \
                                 cluster.bounding_box[1], \
                                 cluster.bounding_box[2], \
                                 fill=False, \
                                 color='white'))

     # On_click definition
    def on_click(event):
        x_position = event.xdata
        y_position = event.ydata
        if x_position != None: # We are not outside the picture
            for cluster in cluster_array:
                if cluster.is_in_bounding(x_position, y_position):
                    axis = event.inaxes
                    text = axis.text(x_position, y_position, cluster.star_name, \
                            fontsize=14, color='white')
                    event.canvas.draw()
                    text.remove()

    # Use event handler
    fig.canvas.mpl_connect('button_release_event', on_click)
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

    # Search the name of the main celestial object
    celestial_objects = library.get_objects(main_cluster_ra, main_cluster_dec, 0.003)
    celestial_objects = {i:celestial_objects[i] for i in celestial_objects if celestial_objects[i] != 'Unknown'}
    key_list = sorted(celestial_objects.keys())
    celestial_key = key_list[0]

    # Write the informations of the transformation matrix on ex4.txt file
    results = 'celestial object: %s' % (celestial_key)
    with open("ex5.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
