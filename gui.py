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


class Gui (kxg.Actor):

    def __init__(self, window):
        kxg.Actor.__init__(self)

        cursor = pyglet.image.load('images/cursor.png')
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
        map_widget = MapWidget(self, self.world.map)

        self.gui.add(viewport)
        viewport.add(map_widget)
        viewport.set_center_of_view(map_widget.rect.center)

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


class MapWidget (glooey.Widget):

    def __init__(self, gui, map):
        super(MapWidget, self).__init__()

        self.gui = gui
        self.map = map
        self.sprites = []

        tileset_path = 'images/open-game-art/outdoor-tileset.png'
        tileset_image = pyglet.resource.image(tileset_path)
        
        self.tileset = pyglet.image.ImageGrid(tileset_image, 6, 16)
        self.tile_width = self.tileset[0].width
        self.tile_height = self.tileset[0].height

        resources_path = 'images/resource-icons.png'
        resources_image = pyglet.resource.image(resources_path)

        self.resources = pyglet.image.ImageGrid(resources_image, 4, 8)
        self.resource_indices = {
                'target':  (3, 0),
                'spiral':  (2, 0),
                'claw':    (1, 0),
                'echelon': (3, 1),
                'chevron': (1, 1),
                'wave':    (0, 1),
                'split':   (3, 2),
                'wheel':   (2, 2),
                'cross':   (1, 2),
                'half':    (1, 3),
                'quarter': (0, 3),
                'chess':   (3, 4),
                'pie':     (2, 4),
                'ridge':   (1, 4),
                'valley':  (0, 4),
                'north':   (3, 5),
                'south':   (2, 5),
                'oculus':  (1, 5),
                'moon':    (0, 5),
                'one':     (3, 6),
                'two':     (2, 6),
                'three':   (1, 6),
        }

    def claim(self):
        self.min_width = self.tile_width * (self.map.columns - 1)
        self.min_height = self.tile_height * (self.map.rows - 1)

    def draw(self):
        self.draw_map()
        self.draw_resources()

    def draw_map(self):
        for row in range(self.map.rows - 1):
            for col in range(self.map.columns - 1):
                terrains = (
                    self.map.tiles[row + 0, col + 0].terrain, # top left
                    self.map.tiles[row + 1, col + 0].terrain, # bottom left
                    self.map.tiles[row + 1, col + 1].terrain, # bottom right
                    self.map.tiles[row + 0, col + 1].terrain, # top right
                )

                # 4 land

                if terrains == ('land', 'land', 'land', 'land'):
                            # empty, flower,  grass,  grass,  grass
                    indices = (4,1), (4,10), (4,11), (5,10), (5,11)
                    weights =    80,      0,      1,      1,      1
                    index = kxg.tools.weighted_choice(indices, weights)

                # 3 land, 1 sea

                elif terrains == ('land', 'land', 'land', 'sea'):
                    index = 4, 3

                elif terrains == ('land', 'land', 'sea', 'land'):
                    index = 5, 3

                elif terrains == ('land', 'sea', 'land', 'land'):
                    index = 5, 4

                elif terrains == ('sea', 'land', 'land', 'land'):
                    index = 4, 4

                # 2 land, 2 sea

                elif terrains == ('land', 'land', 'sea', 'sea'):
                    index = 4, 2

                elif terrains == ('land', 'sea', 'sea', 'land'):
                    index = 3, 1

                elif terrains == ('sea', 'sea', 'land', 'land'):
                    index = 4, 0

                elif terrains == ('sea', 'land', 'land', 'sea'):
                    index = 5, 1

                # 1 land, 3 sea

                elif terrains == ('land', 'sea', 'sea', 'sea'):
                    index = 3, 2

                elif terrains == ('sea', 'sea', 'sea', 'land'):
                    index = 3, 0

                elif terrains == ('sea', 'sea', 'land', 'sea'):
                    index = 5, 0

                elif terrains == ('sea', 'land', 'sea', 'sea'):
                    index = 5, 2

                # 4 sea

                elif terrains == ('sea', 'sea', 'sea', 'sea'):
                    index = 3, 3

                # Diagonal combinations of 2 land and 2 sea are not supported.  

                else:
                    printf('Unsupported tile at {}x{}', row, col)
                    continue

                x, y = self.get_pixel_coords(col, row)

                # It seems like I have to keep references to all my sprites in 
                # order to keep them from getting garbage collected.

                image = self.tileset[index]
                sprite = pyglet.sprite.Sprite(
                        image, x, y, batch=self.batch, group=self.group)
                self.sprites.append(sprite)

    def draw_resources(self):
        for tile in self.map.resource_tiles:
            image_index = self.resource_indices[tile.resource]
            image = self.resources[image_index]
            x, y = self.get_pixel_coords(tile.col, tile.row)

            sprite = pyglet.sprite.Sprite(
                    image, x, y, batch=self.batch, group=self.group)
            self.sprites.append(sprite)

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


class MapExtension:

    def setup(gui):
        map = gui.world.map

        map.setup.connect(self.setup)
        map.setup.disconnect()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 4:
            # Right click
            col, row = self.pixel_to_index_coordinates(x, y)
            tile = self.map[row,col]
            position = vecrec.Vector(col, row)

            if tile.terrain == 'land':
                printf('Building City at index {}', position)
                #message = messages.CreateCity(self.gui.player, position)

            else:
                printf('Cannot build city in the {}', tile.terrain)

    def pixel_to_index_coordinates(self, x, y):
        i = math.floor(x / self.tile_width)
        j = math.floor((self.rect.height - y) / self.tile_height)

        if x == self.map.columns:
            i -=1
        if y == 0:
            j -=1

        return i,j



