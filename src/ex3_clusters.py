#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exercise 3:
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

    # Find the cluster with the greatest integral
    main_clust = mylib.find_main_centroid(cluster_array)

    # Write informations about clusters on ex3.txt file
    results = 'number of clusters: %2d, ' % (len(cluster_array)) \
            + 'greatest integral: %7d, ' % (main_clust.integrated_luminosity) \
            + 'centroid x: %4.1f, centroid y: %4.1f' % \
              (main_clust.centroid_pixel[0], main_clust.centroid_pixel[1])
    with open("ex3.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
