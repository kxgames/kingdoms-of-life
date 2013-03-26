#!/usr/bin/env python

import pyglet
import math

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

points = ()
n = 100
cx, cy = 320, 240
r1, r2 = 220, 150

for i in range(n+2):
    r = r1 if i % 2 else r2
    x = cx + r * math.cos(2 * math.pi * i / n)
    y = cy + r * math.sin(2 * math.pi * i / n)
    points += (x, y)


vertices = batch.add(n+2, pyglet.gl.GL_TRIANGLE_STRIP, None,
    ('v2f', points),
)

@window.event
def on_draw():
    window.clear()
    batch.draw()

pyglet.app.run()
