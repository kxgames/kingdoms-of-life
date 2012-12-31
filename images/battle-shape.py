#!/usr/bin/env python

import sys
sys.path.append('..')

import kxg
import random
import string

vertices = []
iterations = 36
radius = 25
position = 0, 0

for x in range(iterations):
    if x % 2:
        magnitude = radius * random.uniform(0.3, 0.6)
    else:
        magnitude = radius * random.uniform(0.0, 0.1)

    offset = kxg.geometry.Vector.from_degrees(x * 360 / iterations)
    vector = position + (magnitude + radius) * offset 

    vertices.append("%s,%s" % vector.tuple)

print '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'
print '<polygon points="-40,-40 -40,40 40,40 40,-40"/>'
print '<polygon points="%s"/>' % string.join(vertices)
print '</svg>'
