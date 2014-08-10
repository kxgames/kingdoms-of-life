#!/usr/bin/env python

import pyglet

from pyglet.gl import *
from setproctitle import *

window = pyglet.window.Window()
setproctitle('road-demo')

start = 0, 0
end = window.get_size()

@window.event
def on_draw():
    window.clear()

    glColor3f(1.0, 0.5, 0)
    glEnable(GL_BLEND)                                                            
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)                             
    glEnable(GL_LINE_SMOOTH);                                                     
    glLineWidth(3)
    pyglet.graphics.draw(2, GL_LINES, ('v2i', start + end))

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    global start, end

    if button == pyglet.window.mouse.LEFT:
        start = (x, y)

    if button == pyglet.window.mouse.RIGHT:
        end = (x, y)


pyglet.app.run()


