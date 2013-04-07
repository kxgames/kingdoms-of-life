#!/usr/bin/env python

import pyglet
import math

def draw_donut(cx, cy, r1, r2, n=100):
    points = ()

    for i in range(n+2):
        r = r1 if i % 2 else r2
        x = cx + r * math.cos(2 * math.pi * i / n)
        y = cy + r * math.sin(2 * math.pi * i / n)
        points += (x, y)

    points = points[0:2] + points + points[-2:]
    return batch.add(n+4, pyglet.gl.GL_TRIANGLE_STRIP, None, ('v2f', points))


window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

donuts = (
        draw_donut(170, 240, 50, 30),
        draw_donut(320, 240, 50, 30),
        draw_donut(470, 240, 50, 30) )

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_key_release(*args):
    donuts[1].delete()

pyglet.app.run()
