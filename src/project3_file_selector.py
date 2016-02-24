#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Project 3:
Module which allows to change the fits file
which is treated
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import mylib

class Action(object):
    """
    Class which deals both with a radio button and a slider
    """

    def __init__(self, _slider_axis, _fig, _axis):
        """
        Constructor of Action
        """
        self.pixels = None
        self.background = None
        self.dispersion = None
        self.my_widget = None
        self.slider_axis = _slider_axis
        self.fig = _fig
        self.axis = _axis

    def radio_action(self, file_name):
        """
        On click function for radio button
        :param file_name: name of the fits file
        """

        # Get pixels and header from a fits file
        self.pixels, _ = mylib.get_pixels("../data/%s" % (file_name))

        # Process to the fit of the background
        _, _, _, self.background, self.dispersion = mylib.modelling_parameters(self.pixels)

        # Remove the background
        filtered_pixels = mylib.remove_background(self.pixels, self.background, self.dispersion)

        # Update the picture
        self.axis.cla() # delete the previous imshow
        self.axis.imshow(filtered_pixels)
        self.axis.set_title('Use of both slider and radio button')
        self.fig.canvas.draw() # redraw

        # Define the slider widget
        threshold_min = max(0, self.background - 6.0 * self.dispersion)
        threshold_max = self.background + 10.0*self.dispersion
        threshold_init = self.background + 6.0*self.dispersion
        if self.my_widget is not None:
            self.slider_axis.cla()
        self.my_widget = widgets.Slider(self.slider_axis, 'threshold', threshold_min, \
                                   threshold_max, valinit=threshold_init)

    def slider_action(self, threshold):
        """
        On changed function for slider
        :param threshold: value of the threshold
        """
        self.axis.cla() # delete the previous imshow
        filtered_pixels = mylib.remove_background(self.pixels, self.background, \
                          self.dispersion, threshold=threshold)
        self.axis.imshow(filtered_pixels)
        self.axis.set_title('Use of both slider and radio button')
        self.fig.canvas.draw() # redraw

def main():
    """
    Display a fits file choosen by a radio button
    and allows to change the threshold with a slider
    """

    # Display the canvas
    fig, axis = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Get list of fits files
    file_list = []
    for _, _, file_list in os.walk('../data'):
        break
    fits_files = [file_name for file_name in file_list if file_name.split(".")[-1] == "fits"]

    # Define radio button
    radio_axis = plt.axes([0.02, 0.5, 0.2, 0.3])
    radio = widgets.RadioButtons(radio_axis, fits_files)

    # Define slider axis
    slider_axis = plt.axes([0.2, 0.1, 0.6, 0.105])

    # Initialize Action class, display the first fits file
    # and get the slider
    action = Action(slider_axis, fig, axis)
    action.radio_action(fits_files[0])
    my_widget = action.my_widget

    # Use event handler and show
    radio.on_clicked(action.radio_action)
    my_widget.on_changed(action.slider_action)
    plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
