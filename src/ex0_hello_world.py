#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Print message 'Hello, world!'.mv
:Author: LAL npacxx <npacxx@lal.in2p3.fr>
:Date:   February 2016
"""

import sys

# By convention, a function name must contain only lowercase characters and _.
# string=None defines a default value for string and makes it optional.
def print_msg(string=None):
    """Print a message received as an argument or a default message
    if none is passed.
    :param string: a string to print (optional)
    :return: status value (always success, 0)
    """

    if string is None:
        # Define a default message
        string = 'Hello, world!'
    print "%s" % string
    return 0

def print_text(text_list):
    """Print a message from a list of strings
    :param text_list: a list of string to print
    :return: status value (always success, 0)
    """

    print "Your message is:"
    for line in text_list:
        print_msg(line)
    return 0

def merge_text(text_list):
    """Print a message, merging it, from a list of strings
    :param text_list: a list of string to print
    :return: status value (always success, 0)
    """

    print "Your message is:"
    message = ""
    for line in text_list:
        if message != "":
            message += " "
        message += line
    print_msg(message)
    return 0

def enter_text():
    """Take a message entered by the user until the key word '***'
    :return: the message, which is a list of strings
    """

    text_list = [""]
    print "Please enter your message finishing by '***':"
    while text_list[-1] != "***":
        text_list.append(raw_input())

    return text_list[1:-1]

# The following test is considered as a best practice: this way a module
# can be used both as a standalone application or as a module called by another
# module.
if __name__ == "__main__":

    # The main program is implement mainly as a function: this avoids having
    # all the variables used in this context (e.g. string in print_msg) to
    # become global variables.
    status = merge_text(enter_text())

    sys.exit(status)

