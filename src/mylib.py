#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which contains tools for the five exercises
"""

import math
from astropy.io import fits
import numpy as np
# pylint: disable=E
from scipy.optimize import curve_fit
from cluster import Cluster

def get_pixels(path):
    """
    Get a numpy.ndarray corresponding to data
    and an astropy.io.fits.header.Header giving other informations
    from a fits file located at 'path'
    """
    try:
        with fits.open(path) as fits_data:
            return fits_data[0].data, fits_data[0].header
    except IOError:
        print 'cannot open', path
        return None, None

def modelling_function(xvalue, maximum, mean, disp):
    """
    Compute a gaussian function
    :param xvalue: x value
    :param maximum: maximum value
    :param mean: center of the gaussian
    :param disp: dispersion
    :return: gaussian value
    """
    # pylint: disable=E
    return maximum*np.exp(-1./2*(xvalue-mean)*(xvalue-mean)/disp/disp)

def modelling_parameters(pixels):
    """
    Function that takes a 2D array and returns the fit parameters
    :param pixels: 2D array corresponding to the picture
    :return: data values and fitted values
    """
    # Build the pixel distribution
    # pylint: disable=E
    bin_values, bin_boundaries = np.histogram(pixels.ravel(), 200)

    # Normalize the distribution for the gaussian fit
    max_y = np.float(np.max(bin_values))
    normal_y = bin_values/max_y
    max_x = np.float(np.max(bin_boundaries))
    normal_x = bin_boundaries[:-1]/max_x

    # Fit the data with the gaussian modelling function
    # and rescale the parameters
    fit, _ = curve_fit(modelling_function, normal_x, normal_y)
    maxvalue = fit[0] * max_y
    background = fit[1] * max_x
    dispersion = fit[2] * max_x
    dispersion = math.fabs(dispersion)
    x_values = normal_x * max_x
    y_values = normal_y * max_y

    return x_values, y_values, maxvalue, background, dispersion

def remove_background(pixels, background, dispersion, threshold=None):
    """
    Remove the background from the picture
    :param pixels: 2D array corresponding to the picture
    :param background: mean background value
    :param dispersion: dispersion of the background
    :param threshold: set another value for the threshold
    :return: 2D array in which the backgroud has been removed
    """
    if threshold is None: # if the threshold is not already defined
        threshold = background + 6.0 * dispersion
    above = pixels >= threshold
    return above * (pixels - background)

def get_cluster_array(pixels, background, dispersion, threshold=None, my_wcs=None):
    """
    Find the list of clusters in the picture pixels
    according to a threshold defines with background and dispersion
    :param pixels: 2D array corresponding to the picture
    :param background: mean background value
    :param dispersion: dispersion of the background
    :return: list of clusters found in the picture pixels
    """

    # Initiate some variables before looping over all pixels
    if threshold is None:
        threshold = background + 6.0 * dispersion # threshold value
    marks = np.zeros(pixels.shape) # to mark each pixels
    n_row, n_column = pixels.shape
    cluster_array = [] # will contain instances of the class Cluster

    # Loop over pixels and add clusters in cluster_array
    for i in range(n_row):
        for j in range(n_column):
            if marks[i][j] != 1: # if the pixel is not marked
                marks[i][j] = 1 # mark it
                if pixels[i][j] >= threshold: # if luminosity > threshold
                    clust = Cluster()
                    clust.recursive_exploration(i, j, pixels, marks, threshold)
                    clust.find_centroid(my_wcs)
                    cluster_array.append(clust)

    # Return the array of clusters
    return cluster_array

def find_main_centroid(cluster_array):
    """
    Find the cluster with the highest luminosity
    :param cluster_array: contains clusters from the picture
    :return: the cluster of the highest luminosity
    """

    # Loop over the clusters to find to one with the highest luminosity
    greatest_integral = 0
    main_centroid = 0
    for i, clust in enumerate(cluster_array):
        if clust.integrated_luminosity > greatest_integral:
            greatest_integral = clust.integrated_luminosity
            main_centroid = i

    return cluster_array[main_centroid]

