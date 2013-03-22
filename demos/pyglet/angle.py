#!/usr/bin/env python

from __future__ import division

import os
import numpy
import matplotlib.pyplot as plot
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('percent', type=float)
arguments = parser.parse_args()

width, height = 50, 50
y, x = numpy.mgrid[0:width, 0:height]
x -= width / 2
y -= height / 2
angles = numpy.arctan2(-y, x)
bools = angles < numpy.pi * (100 - arguments.percent) / 100

plot.imshow(bools, interpolation='nearest')
plot.colorbar()

if not os.fork(): 
    plot.show()
