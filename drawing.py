#!/usr/bin/env python

from __future__ import division

import math
import pyglet

from kxg import geometry
from numpy import *
import numpy as np

inf = float('inf')
set_printoptions(threshold=inf, linewidth=inf)
# This module will contain code to:
#
# 1. Easily draw fucking circles.
# 2. Draw antialiased lines (slowly).

class Color (object):

    @staticmethod
    def from_hex(hex):
        red, green, blue = int(hex[1:3]), int(hex[3:5]), int(hex[5:7])
        return Color.__init__(red, green, blue)

    @staticmethod
    def from_rgb(red, green, blue):
        return Color.__init__(red, green, blue)

    @staticmethod
    def from_rgb_tuple(rgb):
        return Color.__init__(*rgb)

    @staticmethod
    def from_floats(red, green, blue):
        return Color.__init__(255 * red, 255 * green, 255 * blue)

    @staticmethod
    def from_float_tuple(self, rgb):
        return Color.from_floats(*rgb)


    def __init__(self, red, green, blue):
        self.r = red
        self.g = green
        self.b = blue

    def __iter__(self):
        return iter(self.tuple)

    def __str__(self):
        return '#%02x%02x%02x' % self.tuple

    def __repr__(self):
        return self.__str__()


    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)

    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)

    def __mul__(self, scalar):
        return Color(scalar * self.r, scalar * self.g, scalar * self.b)

    def __div__(self, scalar):
        return Color(self.r / scalar, self.g / scalar, self.b / scalar)


    def get_red(self):
        return self._red

    def get_green(self):
        return self._green

    def get_blue(self):
        return self._blue

    def get_tuple(self):
        return self.r, self.g, self.b
    
    def get_pyglet(self):
        return (self / 255).tuple


    def set_red(self, red):
        self._red = min(max(red, 0), 255)

    def set_green(self, green):
        self._green = min(max(green, 0), 255)

    def set_blue(self, blue):
        self._blue = min(max(blue, 0), 255)

    def set_tuple(self, red, green, blue):
        self.r, self.g, self.b = red, green, blue


    def lighten(self, extent):
        self.interpolate(white, extent)

    def darken(self, extent):
        self.interpolate(black, extent)

    def interpolate(self, target, extent):
        self += extent * (target - self)


    # Properties (fold)
    r = property(get_red, set_red)
    g = property(get_green, set_green)
    b = property(get_blue, set_blue)

    red = property(get_red, set_red)
    green = property(get_green, set_green)
    blue = property(get_blue, set_blue)

    tuple = property(get_tuple)
    pyglet = property(get_pyglet)

    
# Colors (fold)
red = Color(164, 0, 0)
brown = Color(143, 89, 2)
orange = Color(206, 92, 0)
yellow = Color(196, 160, 0)
green = Color(78, 154, 6)
blue = Color(32, 74, 135)
purple = Color(92, 53, 102)
black = Color(46, 52, 54)
gray = Color(85, 87, 83)
white = Color(255, 250, 240)

colors = {
        'red': red,
        'brown': brown,
        'orange': orange,
        'yellow': yellow,
        'green': green,
        'blue': blue,
        'purple': purple,
        'black': black,
        'gray': gray,
        'white': white }


def draw_circle(
        position, radius,
        color=green, num_vertices=100,
        batch=None, group=None, usage='dynamic'):

    from kxg.geometry import Vector

    vertices = ()

    for iteration in range(num_vertices + 1):
        radians = math.pi * iteration / num_vertices
        if iteration % 2: radians *= -1

        vertex = position + radius * Vector.from_radians(radians)
        vertices += vertex.tuple

    vertices = vertices[0:2] + vertices + vertices[-2:]

    if batch is None:
        return graphics.vertex_list(
                num_vertices + 3,
                ('v2f/%' % usage, vertices),
                ('c3B', color.tuple * (num_vertices + 3)))
    else:
        return batch.add(
                num_vertices + 3, pyglet.gl.GL_TRIANGLE_STRIP, group,
                ('v2f', vertices),
                ('c3B', color.tuple * (num_vertices + 3)))

def draw_pretty_line(
        start, end, stroke, color=green,
        batch=None, group=None, usage='static'):

    buffer, origin = _line_to_array(start, end, stroke)
    canvas = ones(buffer.shape + (4,), dtype='uint8')

    canvas[:,:,0] *= color.red
    canvas[:,:,1] *= color.green
    canvas[:,:,2] *= color.blue
    canvas[:,:,3] = 255 * buffer
    
    height, width = canvas.shape[0:2]
    data, stride = canvas.tostring(), canvas.strides[0]
    image = pyglet.image.ImageData(width, height, 'RGBA', data, stride) 

    return pyglet.sprite.Sprite(
            image, x=origin.x, y=origin.y,
            batch=batch, group=group, usage=usage)


def _line_to_array(start, end, stroke):
    direction = end - start
    offset = stroke * direction.orthonormal

    start_plus = start + offset
    start_minus = start - offset
    end_plus = end + offset
    end_minus = end - offset
    
    # Create the canvas.
    # Don't need the canvas, just need the width and height.
    box = geometry.Rectangle.from_points(
            start_plus, start_minus, end_plus, end_minus)

    origin = box.top_left

    buffer = np.empty(box.size_as_int)

    # Draw an anti-aliased line.
    pixels_below = _fill_below(box, start - offset - origin, end - offset - origin)
    pixels_above = _fill_below(box, start + offset - origin, end + offset - origin)

    pixels_right = _fill_below(box, start - offset - origin, start + offset - origin)
    pixels_left = _fill_below(box, end - offset - origin, end + offset - origin)

    return abs(pixels_below - pixels_above) * abs(pixels_left - pixels_right), origin

def _fill_below(box, start, end):
    width, height = box.size_as_int
    size = arange(width), arange(height)
    x, y = meshgrid(*size)

    left, right = x, x + 1
    top, bottom = y, y + 1

    if end.x == start.x:
        return clip(x - end.x, 0, 1)

    if end.y == start.y:
        return clip(y - end.y, 0, 1)

    f = lambda x: slope * x + intercept
    g = lambda y: (y - intercept) / slope

    slope = (end.y - start.y) / (end.x - start.x)
    intercept = end.y - slope * end.x

    crossings = clip(g(top), left, right), clip(g(bottom), left, right)
    enter, exit = minimum(*crossings), maximum(*crossings)

    enter_area = (enter - left) * clip(bottom - f(enter), 0, 1)
    exit_area = (right - exit) * clip(bottom - f(exit), 0, 1)
    line_area =                                     \
            - slope * (exit**2 - enter**2) / 2      \
            + (bottom - intercept) * (exit - enter)

    return enter_area + exit_area + line_area

