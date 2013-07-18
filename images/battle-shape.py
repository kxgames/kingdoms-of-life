#!/usr/bin/env python

import sys
sys.path.append('..')

import kxg
import random
import string
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--campaign', '-c', action='store_true')
arguments = parser.parse_args()

vertices = []
iterations = 36
radius = 25
position = 0, 0

for x in range(iterations):

    if not arguments.campaign:
        if x % 2:
            magnitude = radius * random.uniform(0.3, 0.6)
        else:
            magnitude = radius * random.uniform(0.0, 0.1)
    
    else:
        if x % 2:
            magnitude = radius * random.uniform(0.2, 0.2)
        else:
            magnitude = radius * random.uniform(0.0, 0.1)

    offset = kxg.geometry.Vector.from_degrees(x * 360 / iterations)
    vector = position + (magnitude + radius) * offset 

    vertices.append("%s,%s" % vector.tuple)

print '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'
print '<polygon fill="black" points="-40,-40 -40,40 40,40 40,-40"/>'
print '<polygon fill="white" points="%s"/>' % string.join(vertices)
print '</svg>'
