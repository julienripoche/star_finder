#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which contains the class Cluster
"""

import library

class Cluster(object):
    """
    Class which contains a list of pixels corresponding to a given cluster,
    its integrated luminosity, coordinates of the centroid etc
    """

    def __init__(self):
        """
        Constructor of Cluster
        """
        self.cluster_pixels = []
        self.integrated_luminosity = 0
        self.bounding_box = None
        self.centroid_pixel = None
        self.centroid_wcs = None
        self.star_name = ""

    def append_pixel(self, i, j, pixels):
        """
        Append the pixel to the cluster:
        - append pixel coordinates to the list of pixels
        - add its luminosity to the integrated luminosity
        :param i: abs of the pixel
        :param j: ord of the pixel
        :param pixels: 2D array of pixels
        """
        self.cluster_pixels.append((i, j))
        self.integrated_luminosity += pixels[i][j]

    # Disable the too many arguments comment
    # this is necessary in this recursive approach
    # pylint: disable=R
    def recursive_exploration(self, i, j, pixels, marks, threshold):
        """
        Append the pixel (i,j) and explore the contiguous pixels
        :param i: abs of the pixel
        :param j: ord of the pixel
        :param pixels: 2D array of pixels
        :param marks: 2D array to avoid double couting
        :param threshold: allows to discriminate pixels
        """
        self.append_pixel(i, j, pixels)
        if j != pixels.shape[1] - 1:
            self.threshold_checker(i, j+1, pixels, marks, threshold)
        if i != 0:
            self.threshold_checker(i-1, j, pixels, marks, threshold)
        if j != 0:
            self.threshold_checker(i, j-1, pixels, marks, threshold)
        if i != pixels.shape[0] - 1:
            self.threshold_checker(i+1, j, pixels, marks, threshold)

    # Disable the too many arguments comment
    # this is necessary in this recursive approach
    # pylint: disable=R
    def threshold_checker(self, i, j, pixels, marks, threshold):
        """
        Check if the pixel (i,j) is already treated
        and if it is above the threshold
        :param i: abs of the pixel
        :param j: ord of the pixel
        :param pixels: 2D array of pixels
        :param marks: 2D array to avoid double couting
        :param threshold: allows to discriminate pixels
        """
        if marks[i][j] == 0.:
            marks[i][j] = 1
            if pixels[i][j] >= threshold:
                self.recursive_exploration(i, j, pixels, marks, threshold)

    def find_star_name(self):
        """
        Method to find the name of the celestial object
        given by its WCS position
        """
        # Get the dictionnary of all objects in this region
        celestial_objects = library.get_objects(self.centroid_wcs[0], \
                                                self.centroid_wcs[1], 0.003)

        # If there is some objects in this region
        if len(celestial_objects) != 0:
            knowns_objs = {i:celestial_objects[i] for i in celestial_objects \
                           if celestial_objects[i] != 'Unknown'}
            if len(knowns_objs) != 0:
                knowns_keys = sorted(knowns_objs.keys())
                self.star_name = knowns_keys[0]
            else:
                unknowns = {i:celestial_objects[i] for i in celestial_objects \
                            if celestial_objects[i] == 'Unknown'}
                unknowns_keys = sorted(unknowns.keys())
                self.star_name = unknowns_keys[0]
        else: # is there is no object in this region
            self.star_name = "Unfound"

    def find_centroid(self, my_wcs=None):
        """
        Method that find the centroid coordinates,
        convert them into celestial coordinates
        and find the bounding box of the cluster
        """
        ymin, xmin = self.cluster_pixels[0]
        ymax, xmax = ymin, xmin
        pixels_number = len(self.cluster_pixels)

        # Loop over all pixels to increase the size of the bounding box
        for i in range(pixels_number - 1):
            ypix, xpix = self.cluster_pixels[i + 1]
            if xpix > xmax:
                xmax = xpix
            elif xpix < xmin:
                xmin = xpix
            if ypix > ymax:
                ymax = ypix
            elif ypix < ymin:
                ymin = ypix

        # Determine centroid and boundung box
        self.centroid_pixel = ((xmax+xmin)/2., (ymax+ymin)/2.)
        self.bounding_box = ([xmin-0.5, ymin-0.5], xmax-xmin+1, ymax-ymin+1)

        # If asked, determine wcs coordinates and search for star name
        if my_wcs != None:
            self.centroid_wcs = my_wcs.convert_to_radec( \
                                 self.centroid_pixel[0], \
                                 self.centroid_pixel[1])
            self.find_star_name()

    def is_in_bounding(self, x_position, y_position):
        """
        Return True if (x_position, y_position) is contained
        in the bounding box else False
        """
        x_position = int(x_position)
        y_position = int(y_position)
        if x_position >= self.bounding_box[0][0] and \
           x_position <= self.bounding_box[0][0] + self.bounding_box[1]:
            if y_position >= self.bounding_box[0][1] and \
               y_position <= self.bounding_box[0][1] + self.bounding_box[2]:
                return True
        return False

