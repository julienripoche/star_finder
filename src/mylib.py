#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which contains tools for the five exercises
"""

import logging
import math

import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

import library

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
    Remove the background of the picture
    :param pixels: 2D array corresponding to the picture
    :param background: mean background value
    :param dispersion: dispersion in the background value
    :return: 2D array corresponding to the picture in which the backgroud has been removed
    """
    if threshold == None:
        threshold = background + 6.0 * dispersion
    above = pixels >= threshold
    return above * (pixels - background)

class Cluster():
    """
    Class which contain a list of pixel corresponding to a given cluster,
    its integrated luminosity and the coordinates of the centroid
    """

    def __init__(self, _pixels, _marks, _threshold):
        """
        Constructor of Cluster
        :param _pixels: 2D array corresponding to the picture without the background
        :param _marks: 2D array used to avoid double pixels counting
        :param _threshold: Limit of allowed pixel luminosity
        """
        self.n_row, self.n_column = _pixels.shape
        self.pixels = _pixels
        self.marks = _marks
        self.threshold = _threshold
        self.cluster_pixels = []
        self.integrated_luminosity = 0
        self.centroid_pixel = None
        self.centroid_WCS = None
        self.star_name = ""
        self.bounding_box = None

    def append_pixel(self, i, j):
        """
        Append the pixel to the cluster:
        - append pixel coordinates to the list of pixels
        - add its luminosity to the integrated luminosity
        :param i: abscissa of the pixel
        :param j: ordinate of the pixel
        """
        self.cluster_pixels.append((i, j))
        self.integrated_luminosity += self.pixels[i][j]

    def get_centroid_WCS(self, _centroid_WCS):
        """
        Get the doublet of WCS coordinates associated to the centroid
        :param _centroid_WCS: WCS coordinates of the centroid
        """
        self.centroid_WCS = _centroid_WCS

    def find_centroid(self):
        """
        Method that find the centroid of the cluster
        """
        xmin, ymin = self.cluster_pixels[0]
        xmax, ymax = xmin, ymin
        pixels_number = len(self.cluster_pixels)
        for i in range(pixels_number - 1):
            x, y = self.cluster_pixels[i + 1]
            if x > xmax:
                xmax = x
            elif x < xmin:
                xmin = x
            if y > ymax:
                ymax = y
            elif y < ymin:
                ymin = y
        self.centroid_pixel = ((ymax+ymin)/2., (xmax+xmin)/2.)
        self.bounding_box = ([ymin, xmin], ymax-ymin+1, xmax-xmin+1)

    def marks_updater(self):
        """
        Update the pixel marker
        :return: new pixel marker
        """
        return self.marks

    def cluster_exploration(self, i, j):
        """
        Start the exporation of the cluster and finally find the centroid
        :param i: abscissa of the first pixel of the cluster
        :param j: ordinate of the first pixel of the cluster
        """
        self.recursive_exploration(i, j)
        self.find_centroid()

    def threshold_checker(self, i, j):
        """
        Check if the pixel (i,j) is above the threshold
        :param i: abscissa of the pixel
        :param j: ordinate of the pixel
        """
        if self.marks[i][j] == 0.:
            self.marks[i][j] = 1
            if self.pixels[i][j] >= self.threshold:
                self.recursive_exploration(i, j)

    def recursive_exploration(self, i, j):
        """
        Append the pixel (i,j) and explore the contiguous pixels
        :param i: abscissa of the pixel
        :param j: ordinate of the pixel
        """
        self.append_pixel(i, j)
        if j != self.n_column - 1:
            self.threshold_checker(i, j+1)
        if i != 0:
            self.threshold_checker(i-1, j)
        if j != 0:
            self.threshold_checker(i, j-1)
        if i != self.n_row - 1:
            self.threshold_checker(i+1, j)

    def find_star_name(self):
        celestial_objects = library.get_objects(self.centroid_WCS[0], self.centroid_WCS[1], 0.003)
        if len(celestial_objects) != 0:
            non_unknowns = {i:celestial_objects[i] for i in celestial_objects \
                            if celestial_objects[i] != 'Unknown'}
            non_unknowns_keys = sorted(non_unknowns.keys())
            if len(non_unknowns_keys) != 0:
                self.star_name = non_unknowns_keys[0]
            else:
                unknowns = {i:celestial_objects[i] for i in celestial_objects \
                            if celestial_objects[i] == 'Unknown'}
                unknowns_keys = sorted(unknowns.keys())
                self.star_name = unknowns_keys[0]
        else:
            self.star_name = "Unfound"

    def is_in_bounding(self, x_position, y_position):
        x_position = int(x_position)
        y_position = int(y_position)
        if x_position >= self.bounding_box[0][0] and \
                        x_position <= self.bounding_box[0][0] + self.bounding_box[1]:
            if y_position >= self.bounding_box[0][1] and \
                            y_position <= self.bounding_box[0][1] + self.bounding_box[2]:
                return True
        return False

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
