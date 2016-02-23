#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which contains tools for the five exercises
"""

import math
import logging
from astropy.io import fits
import numpy as np
from scipy.optimize import curve_fit
import library
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
    except:
        print 'cannot open', path
        return None, None

def modelling_function(x, maximum, mean, disp):
    """
    Compute a gaussian function
    :param x: x value
    :param maximum: maximum value
    :param mean: center of the gaussian
    :param disp: dispersion
    :return: gaussian value
    """
    # pylint: disable=E
    return maximum*np.exp(-1./2*(x-mean)*(x-mean)/disp/disp)

def modelling_parameters(pixels):
    """
    Function that takes a 2D array and returns the fit parameters
    :param pixels: 2D array corresponding to the picture
    :return: data values and fitted values
    """
    # Build a flat list of the pixel values
    pixels_flat = pixels.ravel()

    # Build the pixel distribution
    bin_number = 200
    # pylint: disable=E
    bin_values, bin_boundaries = np.histogram(pixels_flat, bin_number)

    # Normalize the distribution for the gaussian fit
    max_y = np.float(np.max(bin_values))
    normal_y = bin_values/max_y
    max_x = np.float(np.max(bin_boundaries))
    normal_x = bin_boundaries[:-1]/max_x

    # Fit the data with the gaussian modelling function and rescale the parameters
    fit, _ = curve_fit(modelling_function, normal_x, normal_y)
    maxvalue = fit[0] * max_y
    background = fit[1] * max_x
    dispersion = fit[2] * max_x
    dispersion = math.fabs(dispersion)
    x = normal_x * max_x
    y = normal_y * max_y

    return x, y, maxvalue, background, dispersion

def remove_background(pixels, background, dispersion, threshold = None):
    """
    Remove the background from the picture
    :param pixels: 2D array corresponding to the picture
    :param background: mean background value
    :param dispersion: dispersion of the background
    :param threshold: set another value for the threshold
    :return: 2D array in which the backgroud has been removed
    """
    if threshold == None: # if the threshold is not already defined
        threshold = background + 6.0 * dispersion
    above = pixels >= threshold
    return above * (pixels - background)

def get_cluster_array(pixels, background, dispersion, my_wcs = None):
    """
    Find the list of clusters in the picture pixels
    according to a threshold defines with background and dispersion
    :param pixels: 2D array corresponding to the picture
    :param background: mean background value
    :param dispersion: dispersion of the background
    :return: list of clusters found in the picture pixels
    """

    # Initiate some variables before looping over all pixels
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
                    clust = Cluster(pixels, marks, threshold)
                    clust.cluster_exploration(i, j)
                    clust.find_centroid(my_wcs)
                    marks = clust.marks_updater()
                    cluster_array.append(clust)

    # Return the array of clusters
    return cluster_array

if __name__ == '__main__':

    # test_Simbad
    objects = library.get_objects(1.0, 1.0, 0.1)
    for obj in objects:
        print '%s (%s)' % (obj, objects[obj])
    if len(objects) != 14:
        print 'error'

    # test_WCS

    header = None
    try:
        with fits.open('../data/dss.19.59.54.3+09.59.20.9 10x10.fits') as data_fits:
            try:
                data_fits.verify('silentfix')
                header = data_fits[0].header
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)

    w = library.WCS(header)
    ra, dec = w.convert_to_radec(0, 0)

    print ra, dec

    if abs(ra - 300.060983768) > 1e-5:
        print 'error'

    if abs(dec - 9.90624639801) > 1e5:
        print 'error'
