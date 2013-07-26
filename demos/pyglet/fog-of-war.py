#!/usr/bin/env python

import pyglet
import math

from pyglet.gl import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

cube = pyglet.image.load('cube.png')
sprite = pyglet.sprite.Sprite(cube, batch=batch)

def draw_donut(cx, cy, r1, r2, n=100):
    points = ()

    for i in range(n+2):
        r = r1 if i % 2 else r2
        x = cx + r * math.cos(2 * math.pi * i / n)
        y = cy + r * math.sin(2 * math.pi * i / n)
        points += (x, y)

    points = points[0:2] + points + points[-2:]
    return pyglet.graphics.draw(
            n+4, pyglet.gl.GL_TRIANGLE_STRIP, ('v2f', points))


@window.event
def on_draw():
    window.clear()

    glClear(GL_DEPTH_BUFFER_BIT);
    glEnable(GL_STENCIL_TEST);
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);
    glDepthMask(GL_FALSE);
    glStencilFunc(GL_NEVER, 1, 0xFF);
    glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP);  # draw 1s on test fail (always)

    glStencilMask(0xFF);
    glClear(GL_STENCIL_BUFFER_BIT);  # needs mask=0xFF

    draw_donut(320, 240, 100, 30)

    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
    glDepthMask(GL_TRUE);
    glStencilMask(0x00);
    glStencilFunc(GL_EQUAL, 1, 0xFF);

    batch.draw()

    glDisable(GL_STENCIL_TEST);

@window.event
def on_mouse_motion(x, y, dx, dy):
    sprite.x = x - sprite.width // 2
    sprite.y = y - sprite.height // 2

pyglet.app.run()
