#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exercise 4:
Module which find WCS coordinates of clusters,
display the picture and show the WCS coordinates
of the pixel given by the mouse
"""

import sys
import matplotlib.pyplot as plt
import mylib
import library

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits,
    find the clusters array, find there WCS coordinates, display it
    """

    # Get pixels and header from a fits file
    pixels, header = mylib.get_pixels("../data/specific.fits")

    # Process to the fit of the background
    _, _, _, background, dispersion = mylib.modelling_parameters(pixels)

    # Get the list of clusters
    my_wcs = library.WCS(header) # Instantiate WCS conversion object
    cluster_array = mylib.get_cluster_array(pixels, background, \
                                            dispersion, my_wcs)

    # Remove the background
    filtered_pixels = mylib.remove_background(pixels, background, dispersion)

    # Display the picture
    fig, axis = plt.subplots()
    axis.imshow(filtered_pixels)

    # Move function definition
    def move(event):
        """
        Function called when the event 'motion_notify_event' occurs,
        the wcs coordinates of the pixel pointed by the mouse are
        then displayed at its location
        """
        x_position = event.xdata
        y_position = event.ydata
        if x_position != None: # if we are not outside the picture
            rad, dec = my_wcs.convert_to_radec(x_position, y_position)
            text = axis.text(x_position, y_position, 'ra: %.6f, dec: %.6f' % \
                            (rad, dec), fontsize=14, color='white')
            event.canvas.draw()
            text.remove()

    # Use event handler
    fig.canvas.mpl_connect('motion_notify_event', move)
    plt.show()

    # Find the cluster with the greatest integral
    main_clust = mylib.find_main_centroid(cluster_array)

    # Write informations about WCS coordinates on ex4.txt file
    results = 'right ascension: %.3f, declination: %.3f' % \
              (main_clust.centroid_wcs[0], main_clust.centroid_wcs[1])
    with open("ex4.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
