#!/usr/bin/env python
# encoding: utf-8

# Imports (fold)
import kxg
import tokens
import messages
import drawing
import arguments

import glooey
import math
import numpy
import operator
import pyglet
import random
import vecrec

from pyglet.graphics import OrderedGroup
from kxg.tools import printf
from vecrec import Vector


# Annoyances
# ==========
# 1. The token extension and the game widget get created at different times, 
#    and it makes it hard to initialize either one.

class Gui (kxg.Actor):

    def __init__(self, window):
        kxg.Actor.__init__(self)

        cursor = pyglet.image.load('images/gui/cursor.png')
        hotspot = 4, 24

        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.gui = glooey.PanningGui(window, cursor, hotspot, batch=self.batch)

        self.world = None
        self.player = None
        self.selection = None
        self.play_again = False
        self.finished = False

        self.frame_rate = pyglet.clock.ClockDisplay()
    
    def get_name(self):
        return 'gui'

    def get_world(self):
        return self.world

    def postgame_finished(self):
        return self.finished

    def setup(self, world):
        self.world = world
        self.player = None
        self.selection = None
        self.finished = False
        self.play_again = False

    def setup_pregame(self):
        width, height = 500, 500

        self.window.set_size(width, height)
        self.window.set_visible(True)

        self.pregame_message = pyglet.text.Label(
                "Waiting for players...",
                color=(255, 255, 255, 255),
                font_name='Deja Vu Sans', font_size=32,
                x=width//2, y=height//2,
                anchor_x='center', anchor_y='center',
                batch=self.batch)

    def setup_game(self):
        self.teardown_pregame()

        viewport = glooey.Viewport()
        self.widget = GameWidget(self, self.world)
        self.gui.add(viewport)
        viewport.add(self.widget)
        viewport.set_center_of_view(self.widget.rect.center)

    def setup_postgame(self):
        pass

    def update(self, time):
        pass

    def update_background(self):
        if not self.player:
            pyglet.gl.glClearColor(0, 0, 0, 1)
            return

        background_color = [x / 255 for x in colors['background']] + [1]
        pyglet.gl.glClearColor(*background_color)

    def teardown_pregame(self):
        self.pregame_message.delete()

    def teardown(self):
        pass

    def teardown_postgame(self):
        pass

    def handle_start_game(self, message, is_mine):
        self.setup_game()


class GameWidget (glooey.Widget):

    def __init__(self, gui, world):
        super(GameWidget, self).__init__()
        self.gui = gui
        self.world = world

    def claim(self):
        self.min_width = self.world.map.get_extension(self.gui).rect.width
        self.min_height = self.world.map.get_extension(self.gui).rect.height

    def draw(self):
        self.world.map.get_extension(self.gui).draw()


class MapExtension:

    class NoBleedingGroup(pyglet.graphics.Group):

        def __init__(self, parent=None):
            super(MapExtension.NoBleedingGroup, self).__init__(parent)

        def set_state(self):
            import pyglet.gl as gl
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glTexParameteri(
                    gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        def unset_state(self):
            import pyglet.gl as gl
            gl.glDisable(gl.GL_TEXTURE_2D)


    def __init__(self, gui, map):
        self.gui = gui
        self.map = map
        self.sprites = []   # Just for preventing garbage collection.

        tileset_path = 'images/tilesets/terrain.png'
        tileset_image = pyglet.resource.image(tileset_path)
        
        self.tileset = pyglet.image.ImageGrid(tileset_image, 32, 32)
        self.tile_width = self.tileset[0].width
        self.tile_height = self.tileset[0].height

        width = self.tile_width * (self.map.columns - 1)
        height = self.tile_height * (self.map.rows - 1)

        self.rect = vecrec.Rect.from_size(width, height)

    def draw(self):
        self.ocean_group = self.gui.widget.group
        self.land_group = MapExtension.NoBleedingGroup(self.gui.widget.group)

        self.draw_ocean()
        self.draw_land()

    def draw_ocean(self):
        color = glooey.drawing.Color.from_hex('#156C99')
        sprite = glooey.drawing.draw_rectangle(
                self.gui.widget.rect, color=color,
                batch=self.gui.widget.batch, group=self.ocean_group)
        self.sprites.append(sprite)

    def draw_land(self):
        desert_indices = self.index_climate(20, 18)
        tundra_indices = self.index_climate(14, 18)
        shore_indices = self.index_climate(26, 27)
        grass_indices = self.index_climate(20, 3)
        dirt_indices = self.index_climate(26, 0)

        self.draw_terrain(dirt_indices, lambda x: x != 'water')
        self.draw_terrain(desert_indices, lambda x: x == 'desert')
        self.draw_terrain(tundra_indices, lambda x: x == 'tundra')
        self.draw_terrain(grass_indices, lambda x: x == 'grass')
        self.draw_terrain(shore_indices, lambda x: x == 'water')

    def draw_terrain(self, indices, condition):
        for row in range(self.map.rows - 1):
            for col in range(self.map.columns - 1):
                corners = [
                        (row + 0, col + 0), # top left
                        (row + 1, col + 0), # bottom left
                        (row + 1, col + 1), # bottom right
                        (row + 0, col + 1), # top right
                ]
                climates = [
                        self.map.tiles[corner].climate
                        for corner in corners
                ]
                key = ''.join(
                        'x' if condition(climate) else ' '
                        for climate in climates
                )

                index = indices.get(key)
                x, y = self.get_pixel_coords(col, row)

                if index is None:
                    continue

                # It seems like I have to keep references to all my sprites in 
                # order to keep them from getting garbage collected.

                image = self.tileset[index]
                sprite = pyglet.sprite.Sprite(
                        image, x, y,
                        batch=self.gui.widget.batch,
                        group=self.land_group)
                self.sprites.append(sprite)

    def index_climate(self, row, col):
        return {
                'xxxx': (row + 2, col + 1),
                'xxx ': (row + 4, col + 1),
                'xx x': (row + 5, col + 1),
                'x xx': (row + 5, col + 2),
                ' xxx': (row + 4, col + 2),
                'xx  ': (row + 2, col + 2),
                'x  x': (row + 1, col + 1),
                '  xx': (row + 2, col + 0),
                ' xx ': (row + 3, col + 1),
                '   x': (row + 1, col + 0),
                '  x ': (row + 3, col + 0),
                ' x  ': (row + 3, col + 2),
                'x   ': (row + 1, col + 2),
        }

    @vecrec.accept_anything_as_vector
    def get_world_coords(self, pixel_coords):
        x = pixel_coords.x / self.tile_height
        y = (self.rect.height - pixel_coords.y) / self.tile_height - 1
        return Vector(x, y)

    @vecrec.accept_anything_as_vector
    def get_pixel_coords(self, world_coords):
        x = world_coords.x * self.tile_width
        y = self.rect.height - (world_coords.y + 1) * self.tile_height
        return Vector(x, y)


class SpeciesExtension:

    def __init__(self, gui, species):
        self.gui = gui
        self.species = species

    def draw(self):
        pass



