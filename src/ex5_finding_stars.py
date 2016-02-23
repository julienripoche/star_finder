#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exercise 5:
Module which find name of star in clusters,
display the picture, draw bounding box around clusters
and allow to click on a cluster to have access to
the name of the corresponding celestial object
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import mylib
import library

def main():
    """
    Take datas (2D numpy.array) from the fits file specific.fits,
    find the clusters array, find there names, display it
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

    # Put bounding boxes
    for cluster in cluster_array:
        axis.add_patch(patches.Rectangle(cluster.bounding_box[0], \
                                         cluster.bounding_box[1], \
                                         cluster.bounding_box[2], \
                                         fill=False, \
                                         color='white'))

    # On_click function definition
    def on_click(event):
        """
        Function called when the event 'button_release_event' occurs,
        if the click was made on a bounding box, the name of the
        corresponding celestial object is displayed
        """
        x_position = event.xdata
        y_position = event.ydata
        if x_position != None: # if we are not outside the picture
            for clust in cluster_array:
                if clust.is_in_bounding(x_position, y_position):
                    text = axis.text(x_position, y_position, clust.star_name, \
                                     fontsize=14, color='white')
                    event.canvas.draw()
                    text.remove()

    # Use event handler
    fig.canvas.mpl_connect('button_release_event', on_click)
    plt.show()

    # Find the cluster with the greatest integral
    main_clust = mylib.find_main_centroid(cluster_array)

    # Write the name of the main celestial object on ex5.txt file
    results = 'celestial object: %s' % (main_clust.star_name)
    with open("ex5.txt", 'w') as output_file:
        output_file.write(results)

    return 0

if __name__ == '__main__':
    sys.exit(main())
