from __future__ import division

def gaussian(x, mean, stddev):
    dx = x - mean
    return exp(-0.5 * dx**2 / stddev)

def sigmoid(x, inflection, breadth):
    dx = x - inflection
    return 1 / (1 + exp(-breadth * dx))
