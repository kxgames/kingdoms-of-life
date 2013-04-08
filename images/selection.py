#!/usr/bin/env python

import sys
sys.path.append('..')

import kxg
import random
import string
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--skip', '-k', action='store_true')
arguments = parser.parse_args()

vertices = []
iterations = 36
radius = 32
position = 0, 0

print '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'

for x in range(iterations):
    if arguments.skip and x % 2:
        continue

    offset = kxg.geometry.Vector.from_degrees(x * 360 / iterations)
    vector = position + (radius * offset)
    print '<circle cx="%f" cy="%f" r="1.5"/>' % vector.tuple

print '</svg>'
