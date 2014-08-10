#!/usr/bin/env python

import pyglet
import math

from pyglet.gl import *
from pyglet.graphics import OrderedGroup

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class StencilGroup (OrderedGroup):

    def __init__(self, order, parent=None):
        OrderedGroup.__init__(self, order, parent)

    def set_state(self):
        from pyglet.gl import GL_STENCIL_TEST
        from pyglet.gl import GL_STENCIL_BUFFER_BIT
        from pyglet.gl import GL_DEPTH_BUFFER_BIT

        pyglet.gl.glEnable(GL_STENCIL_TEST)
        pyglet.gl.glClear(GL_DEPTH_BUFFER_BIT)
        pyglet.gl.glClear(GL_STENCIL_BUFFER_BIT)

    def unset_state(self):
        from pyglet.gl import GL_STENCIL_TEST
        pyglet.gl.glDisable(GL_STENCIL_TEST)


class StencilMask (OrderedGroup):

    def __init__(self, order, parent=None):
        OrderedGroup.__init__(self, order, parent)

    def set_state(self):
        from pyglet.gl import GL_FALSE, GL_NEVER
        from pyglet.gl import GL_REPLACE, GL_KEEP

        pyglet.gl.glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        pyglet.gl.glDepthMask(GL_FALSE)
        pyglet.gl.glStencilFunc(GL_NEVER, 1, 0xFF)
        pyglet.gl.glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)

        pyglet.gl.glStencilMask(0xFF)

    def unset_state(self):
        from pyglet.gl import GL_TRUE
        pyglet.gl.glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        pyglet.gl.glDepthMask(GL_TRUE);

class WhereStencilIs (OrderedGroup):

    def __init__(self, order, parent=None):
        OrderedGroup.__init__(self, order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00)
        pyglet.gl.glStencilFunc(GL_EQUAL, 1, 0xFF)

    def unset_state(self):
        pass


class WhereStencilIsnt (OrderedGroup):

    def __init__(self, order, parent=None):
        OrderedGroup.__init__(self, order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00);
        pyglet.gl.glStencilFunc(GL_EQUAL, 0, 0xFF)

    def unset_state(self):
        pass



bottom_group = OrderedGroup(1)
stencil_group = StencilGroup(2)
mask_group = StencilMask(3, stencil_group)
red_cube_group = WhereStencilIs(4, stencil_group)
blue_cube_group = WhereStencilIsnt(5, stencil_group)
top_group = OrderedGroup(6)

def draw_donut(cx, cy, r1, r2, batch, group):
    points = ()
    n = 100

    for i in range(n+2):
        r = r1 if i % 2 else r2
        x = cx + r * math.cos(2 * math.pi * i / n)
        y = cy + r * math.sin(2 * math.pi * i / n)
        points += (x, y)

    points = points[0:2] + points + points[-2:]
    return batch.add(
            n+4, GL_TRIANGLE_STRIP, group, ('v2f', points))


draw_donut(320, 240, 100, 30, batch=batch, group=mask_group)

blue_cube = pyglet.image.load('blue-cube.png')
blue_sprite = pyglet.sprite.Sprite(blue_cube, batch=batch, group=blue_cube_group)

red_cube = pyglet.image.load('red-cube.png')
red_sprite = pyglet.sprite.Sprite(red_cube, batch=batch, group=red_cube_group)

draw_donut(160, 120, 40, 10, batch=batch, group=top_group)
draw_donut(480, 360, 40, 10, batch=batch, group=bottom_group)

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    x = x - blue_sprite.width // 2
    y = y - blue_sprite.height // 2

    blue_sprite.x = x
    blue_sprite.y = y

    red_sprite.x = x
    red_sprite.y = y


pyglet.app.run()


