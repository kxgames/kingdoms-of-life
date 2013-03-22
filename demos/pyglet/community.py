#!/usr/bin/env python

from __future__ import division

import math
import numpy
import pyglet

from pylab import *
from pyglet.gl import *
from setproctitle import *

class Manager:

    colors = {            # (fold)
            'red':          (164,   0,   0),
            'brown':        (143,  89,   2),
            'orange':       (206,  92,   0),
            'yellow':       (196, 160,   0),
            'green':        ( 78, 154,   6),
            'blue':         ( 32,  74, 135),
            'purple':       ( 92,  53, 102),
            'black':        ( 46,  52,  54),
    }


    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.bin = pyglet.image.atlas.TextureBin()

        self.map_layer = pyglet.graphics.OrderedGroup(0)
        self.road_layer = pyglet.graphics.OrderedGroup(1)
        self.city_layer = pyglet.graphics.OrderedGroup(2)
        self.army_layer = pyglet.graphics.OrderedGroup(3)

        self.army_icon = self.load_icon('images/army-icon.png')
        self.city_icon = self.load_icon('images/city-icon.png')

        self.normal_shape = self.load_team_icon('images/normal-shape.png')
        self.battle_shape = self.load_team_icon('images/battle-shape.png')

        self.health_bar = self.load_health_icon('images/full-health.png', 25)
        self.health_outline = self.load_icon('images/empty-health.png')

    def update(self):
        glClearColor(255, 250, 240, 255)
        self.batch.draw()


    def path_to_array(self, path):
        buffer = 255 * imread(path)
        buffer = buffer.astype('uint8')
        return buffer

    def array_to_texture(self, buffer):
        width, height = buffer.shape[0:2]
        data, stride = buffer.tostring(), -buffer.strides[0]
        image = pyglet.image.ImageData(width, height, 'RGBA', data, stride) 
        return self.bin.add(image)


    def load_icon(self, path):
        buffer = self.path_to_array(path)

        buffer[:,:,3] = buffer[:,:,0]
        buffer[:,:,0:3] = 255

        return self.array_to_texture(buffer)

    def load_team_icon(self, path):
        master_buffer = self.path_to_array(path)
        colored_icons = {}

        for name in self.colors:
            red, green, blue = self.colors[name]
            buffer = master_buffer.copy()
            
            buffer[:,:,3] = buffer[:,:,0]
            buffer[:,:,0] = red
            buffer[:,:,1] = green
            buffer[:,:,2] = blue

            colored_icons[name] = self.array_to_texture(buffer)

        return colored_icons

    def load_health_icon(self, path, frames):
        master_buffer = self.path_to_array(path)
        health_bar = []

        width, height = master_buffer.shape[0:2]
        y, x = numpy.mgrid[0:width, 0:height]
        angles = numpy.arctan2(height//2 - y, x - width//2)

        for index in range(frames):
            percent = index / (frames - 1)
            threshold = numpy.pi * (1 - percent)

            buffer = master_buffer.copy()
            buffer[:,:,3] = buffer[:,:,0] * (angles >= threshold)
            buffer[:,:,0:3] = 255

            frame = self.array_to_texture(buffer)
            health_bar.append(frame)

        return health_bar


class CommunityIcon:

    def __init__(self, manager, x, y, color):
        self.manager = manager
        self.position = x, y
        self.target = None
        self.color = color
        self.level = 1
        self.fighting = False
        self.max_health = 100
        self.health = self.max_health

        batch = manager.batch
        layer = self.get_layer()
        back = pyglet.graphics.OrderedGroup(0, parent=layer)
        front = pyglet.graphics.OrderedGroup(1, parent=layer)
        dummy_icon = pyglet.image.ImageData(0, 0, 'RGBA', 0)

        self.icon = pyglet.sprite.Sprite(
                self.get_icon(), x=x, y=y, batch=batch, group=front)
        self.shape = pyglet.sprite.Sprite(
                manager.normal_shape[color], x=x, y=y, batch=batch, group=back)
        self.health_bar = pyglet.sprite.Sprite(
                manager.health_bar[-1], x=x, y=y, batch=batch, group=front)
        self.health_outline = pyglet.sprite.Sprite(
                manager.health_outline, x=x, y=y, batch=batch, group=front)
        self.level_label = pyglet.text.Label("1",
                font_name='Deja Vu Sans Bold', font_size=14,
                color=(255, 255, 255, 255),
                anchor_x='center', anchor_y='center',
                x=(x + 40),
                y=(y + 50.25),
                group=front, batch=batch)


    def update(self, time):
        pass

    def select(self):
        pass

    def move(self, dx, dy):
        x, y = self.position
        self.position = x + dx, y + dy

        self.icon.position = self.position
        self.shape.position = self.position
        self.health_bar.position = self.position
        self.health_outline.position = self.position

        self.level_label.x = self.position[0] + 40
        self.level_label.y = self.position[1] + 50.25

    def damage(self, delta):
        self.health = max(self.health - delta, 0)
        self._update_health()
        
    def repair(self, delta):
        self.health = min(self.health + delta, self.max_health)
        self._update_health()

    def upgrade(self):
        self.level += 1
        self.level_label.text = str(self.level)

    def enter_battle(self):
        self.fighting = True
        self.shape.image = self.manager.battle_shape[self.color]

    def exit_battle(self):
        self.fighting = False
        self.shape.image = self.manager.normal_shape[self.color]


    def _update_health(self):
        animation = self.manager.health_bar
        max_index = len(animation) - 1
        index = max_index * self.health // self.max_health
        self.health_bar.image = animation[index]


class CityIcon (CommunityIcon):

    def get_layer(self):
        return self.manager.army_layer

    def get_icon(self):
        return self.manager.city_icon


class ArmyIcon (CommunityIcon):

    def update(self, time):
        if self.target is None:
            return

        sx, sy = self.position
        tx, ty = self.target

        dx = tx - sx
        dy = ty - sy

        speed = 70
        distance = sqrt(dx**2 + dy**2)
        magnitude = speed * time / distance

        if distance < 1:
            self.target = None

        dx, dy = magnitude * dx, magnitude * dy
        self.move(dx, dy)

    def get_layer(self):
        return self.manager.army_layer

    def get_icon(self):
        return self.manager.army_icon


window = pyglet.window.Window()
fps_display = pyglet.clock.ClockDisplay()

manager = Manager()
selection = None
cities = []

colors = 'purple', 'orange'
color = colors[0]


def update(time):
    for city in cities:
        city.update(time)

@window.event
def on_draw():
    window.clear()
    manager.update()

@window.event
def on_mouse_release(x, y, button, modifiers):
    x -= 40
    y -= 40

    global selection

    if selection and button == pyglet.window.mouse.MIDDLE:
        selection.target = x, y

    else:
        selection = None
        closest_distance = float('inf')

        for city in cities:
            rx, ry = city.position
            distance_squared = (x - rx)**2 + (y - ry)**2
            distance = math.sqrt(distance_squared)

            if distance < closest_distance:
                closest_distance = distance
                closest_city = city

        if button == pyglet.window.mouse.LEFT:
            if closest_distance < 40:
                selection = closest_city

            if closest_distance > 100:
                selection = CityIcon(manager, x, y, color)
                cities.append(selection)

        if button == pyglet.window.mouse.RIGHT:
            if closest_distance > 100:
                selection = ArmyIcon(manager, x, y, color)
                cities.append(selection)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    delta = 3 * abs(scroll_y)

    if not selection:
        return
    if scroll_y < 0:
        selection.repair(delta)
    if scroll_y > 0:
        selection.damage(delta)

@window.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.TAB:
        global color
        global colors

        colors = colors[1], colors[0]
        color = colors[0]

    if selection and symbol == pyglet.window.key.SPACE: 
        selection.upgrade()

    if selection and symbol == pyglet.window.key.ENTER:
        if not selection.fighting:
            selection.enter_battle()
        else:
            selection.exit_battle()


pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()


