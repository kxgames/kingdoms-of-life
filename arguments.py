import argparse

# This module provides a convenient way to interact with options specified on 
# the command line.  Core options can be defined in this file, but additional 
# options can be defined on a per-script basis.  For example, the client script 
# defines a host argument.
#
# Once the parse_args() function is called, new arguments can no longer be 
# added.  Each script should call this function at some point, otherwise the 
# command-line will never be read.  Any arguments can be accessed directly 
# through this module.

parser = argparse.ArgumentParser()
parser.add_argument('--wealthy', '-w', action='store_true')
parser.add_argument('--fps', '-f', action='store_true')

def parse_args():
    arguments = parser.parse_args()
    globals().update(vars(arguments))

