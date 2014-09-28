#!/usr/bin/env python

import pyglet
import math

window = pyglet.window.Window(500, 500)
batch = pyglet.graphics.Batch()

pyglet.resource.path = ['images']
pyglet.resource.reindex()

tileset_path = 'tilesets/terrain.png'
tileset_image = pyglet.resource.image(tileset_path)
tileset_grid = pyglet.image.ImageGrid(tileset_image, 32, 32)
tileset_tex = pyglet.image.Texture3D.create_for_image_grid(tileset_grid)

sprite = pyglet.sprite.Sprite(
        tileset_grid[32*20], 250, 250, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()

pyglet.app.run()

