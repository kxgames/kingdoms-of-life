#!/usr/bin/env python
# encoding: utf-8

import kxg
import tokens
import messages
import drawing
import arguments

import math
import numpy
import pyglet
import operator
import random

from pyglet.graphics import OrderedGroup
from kxg.tools import printf

class Gui (kxg.Actor):

    def __init__(self, window):
        kxg.Actor.__init__(self)

        self.window = window

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
        handlers = PregameHandlers(self)

        self.window.set_size(width, height)
        self.window.set_visible(True)
        self.window.push_handlers(handlers)

        self.batch = pyglet.graphics.Batch()

        self.pregame_message = pyglet.text.Label(
                "Waiting for players...",
                color=(255, 255, 255, 255),
                font_name='Deja Vu Sans', font_size=42,
                x=width//2, y=height//2,
                anchor_x='center', anchor_y='center',
                batch=self.batch)

    def setup_game(self):
        self.teardown_pregame()

        handlers = GameHandlers(self)
        self.window.push_handlers(handlers)

    def setup_postgame(self):
        handlers = PostgameHandlers(self)
        self.window.push_handlers(handlers)


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
        self.window.pop_handlers()

    def teardown(self):
        self.window.pop_handlers()

    def teardown_postgame(self):
        self.window.pop_handlers()


    def handle_start_game(self, message, is_mine):
        self.setup_game()


    def show_error(self, message):
        print(message.error)



class MapExtension (kxg.TokenExtension):

    # For big map:  Keep track of viewport.  As viewport moves, change 
    # visibility of the tile sprites so that only sprites within the viewport 
    # are visible.

    def __init__(self, gui, map):
        self.gui = gui
        self.map = map
        self.sprites = []

        tileset_path = 'images/open-game-art/outdoor-tileset.png'
        tileset_image = pyglet.resource.image(tileset_path)
        tileset = pyglet.image.ImageGrid(tileset_image, 6, 16)

        window_width = gui.window.width
        window_height = gui.window.height
        tile_width = tileset[0].width       # All tiles are the same size.
        tile_height = tileset[0].height

        # Make a sprite for each tile.

        for row in range(map.rows - 1):
            for col in range(map.columns - 1):
                terrains = (
                    map.tiles[row + 0, col + 0].terrain, # top left
                    map.tiles[row + 0, col + 1].terrain, # bottom left
                    map.tiles[row + 1, col + 1].terrain, # bottom right
                    map.tiles[row + 1, col + 0].terrain, # top right
                )

                # 4 land

                if terrains == ('land', 'land', 'land', 'land'):
                    ##         empty, flower,  grass,  grass,  grass
                    #indices = (4,1), (4,10), (4,11), (5,10), (5,11)
                    #weights =    80,      3,     10,     10,     10
                    #index = kxg.tools.weighted_choice(indices, weights)
                    index = 4, 1

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
                    printf('Unsupported tile at {}x{}', row, column)
                    continue

                x = row * tile_width
                y = window_height - (col + 1) * tile_height

                # It seems like I have to keep references to all my sprites in 
                # order to keep them from getting garbage collected.

                image = tileset[index]
                sprite = pyglet.sprite.Sprite(image, x, y, batch=gui.batch)
                self.sprites.append(sprite)


    def draw_on_map(self):
        pass

    def draw_on_minimap(self):
        pass



class BaseHandlers:

    def __init__(self, gui):
        self.gui = gui

    def on_draw(self):
        self.gui.window.clear()
        self.gui.update_background()
        self.gui.batch.draw()

        if arguments.fps:
            self.gui.frame_rate.draw()


class PregameHandlers (BaseHandlers):

    def __init__(self, gui):
        BaseHandlers.__init__(self, gui)


class GameHandlers (BaseHandlers):

    def __init__(self, gui):
        BaseHandlers.__init__(self, gui)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        position = kxg.geometry.Vector(x, y)
        
        if button == pyglet.window.mouse.LEFT:
            pass

    def on_mouse_release(self, x, y, button, modifiers):
        position = kxg.geometry.Vector(x, y)
        
        if button == pyglet.window.mouse.LEFT:
            pass

        if button == pyglet.window.mouse.RIGHT:
            pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.F:
            pass
        if symbol == pyglet.window.key.D:
            pass
        if symbol == pyglet.window.key._1:
            pass
        if symbol == pyglet.window.key.SPACE and self.gui.selection:
            pass
        if symbol == pyglet.window.key.BACKSPACE and self.gui.selection:
            pass
        if symbol == pyglet.window.key.ESCAPE:
            pass


class PostgameHandlers (BaseHandlers):

    def __init__(self, gui):
        BaseHandlers.__init__(self, gui)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.gui.play_again = True
            self.gui.finished = True
        if symbol == pyglet.window.key.ESCAPE:
            self.gui.play_again = False
            self.gui.finished = True
            return True



