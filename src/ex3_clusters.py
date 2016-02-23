#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module which find clusters in the picture using recursive functions
"""

import sys
import mylib

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits
    and find cluster of pixels in which each pixel has a luminosity
    greater than a threshold (linked to the value of the background)
    """

    # Get pixels and header from a fits file
    pixels, _ = mylib.get_pixels("../data/specific.fits")

    # Process to the fit of the background
    _, _, _, background, dispersion = mylib.modelling_parameters(pixels)

    # Get the list of clusters
    cluster_array = mylib.get_cluster_array(pixels, background, dispersion)

    # Find the number of clusters, the greatest integral
    # and the associated centroid
    clusters_number = len(cluster_array)
    greatest_integral = 0
    centroid_coords = None
    for clust in cluster_array:
        if clust.integrated_luminosity > greatest_integral:
            greatest_integral = clust.integrated_luminosity
            centroid_coords = clust.centroid_pixel

    # Write informations about clusters on ex3.txt file
    results = 'number of clusters: %2d, ' % (clusters_number) \
            + 'greatest integral: %7d, ' % (greatest_integral) \
            + 'centroid x: %4.1f, centroid y: %4.1f' % \
              (centroid_coords[0], centroid_coords[1])
    with open("ex3.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
