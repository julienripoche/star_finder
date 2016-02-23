#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which contains the class Cluster
"""

import library

class Cluster():
    """
    Class which contains a list of pixels corresponding to a given cluster,
    its integrated luminosity, coordinates of the centroid...
    """

    def __init__(self, _pixels, _marks, _threshold):
        """
        Constructor of Cluster
        :param _pixels: 2D array corresponding to the picture
        :param _marks: 2D array used to avoid double pixels counting
        :param _threshold: limit of allowed pixel luminosity
        """
        self.pixels = _pixels
        self.marks = _marks
        self.threshold = _threshold
        self.n_row, self.n_column = _pixels.shape
        self.cluster_pixels = []
        self.integrated_luminosity = 0
        self.bounding_box = None        
        self.centroid_pixel = None
        self.centroid_WCS = None
        self.star_name = ""

    def append_pixel(self, i, j):
        """
        Append the pixel to the cluster:
        - append pixel coordinates to the list of pixels
        - add its luminosity to the integrated luminosity
        :param i: abs of the pixel
        :param j: ord of the pixel
        """
        self.cluster_pixels.append((i, j))
        self.integrated_luminosity += self.pixels[i][j]

    def recursive_exploration(self, i, j):
        """
        Append the pixel (i,j) and explore the contiguous pixels
        :param i: abs of the pixel
        :param j: ord of the pixel
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

    def threshold_checker(self, i, j):
        """
        Check if the pixel (i,j) is already treated
        and if it is above the threshold
        :param i: abs of the pixel
        :param j: ord of the pixel
        """
        if self.marks[i][j] == 0.:
            self.marks[i][j] = 1
            if self.pixels[i][j] >= self.threshold:
                self.recursive_exploration(i, j)

    def cluster_exploration(self, i, j):
        """
        Start the exploration of the cluster
        :param i: abs of the first pixel of the cluster
        :param j: ord of the first pixel of the cluster
        """
        self.recursive_exploration(i, j)

    def find_star_name(self):
        """
        Method to find the name of the celestial object
        given by its WCS position
        """
        # Get the dictionnary of all objects in this region
        celestial_objects = library.get_objects(self.centroid_WCS[0], \
                                                self.centroid_WCS[1], 0.003)
        
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

    def find_centroid(self, my_wcs = None):
        """
        Method that find the centroid coordinates,
        convert them into celestial coordinates
        and find the bounding box of the cluster
        """
        ymin, xmin = self.cluster_pixels[0]
        ymax, xmax = ymin, xmin
        pixels_number = len(self.cluster_pixels)
        for i in range(pixels_number - 1):
            y, x = self.cluster_pixels[i + 1]
            if x > xmax:
                xmax = x
            elif x < xmin:
                xmin = x
            if y > ymax:
                ymax = y
            elif y < ymin:
                ymin = y
        self.centroid_pixel = ((xmax+xmin)/2., (ymax+ymin)/2.)
        self.bounding_box = ([xmin, ymin], xmax-xmin+1, ymax-ymin+1)
        if my_wcs != None:
            self.centroid_WCS = my_wcs.convert_to_radec( \
                                 self.centroid_pixel[0], \
                                 self.centroid_pixel[1])
            self.find_star_name()

    def marks_updater(self):
        """
        Update the pixel marker
        :return: new pixel marker
        """
        return self.marks

    def is_in_bounding(self, x_position, y_position):
        x_position = int(x_position)
        y_position = int(y_position)
        if x_position >= self.bounding_box[0][0] and \
                        x_position <= self.bounding_box[0][0] + self.bounding_box[1]:
            if y_position >= self.bounding_box[0][1] and \
                            y_position <= self.bounding_box[0][1] + self.bounding_box[2]:
                return True
        return False

