#!/usr/bin/env python

from __future__ import division

import kxg
import messages

import math
import numpy
import pyglet

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


class Gui (kxg.Actor):

    def __init__(self, window):
        kxg.Actor.__init__(self)

        self.player = None
        self.selection = None

        self.window = window
        self.window.set_handlers(self)

        self.batch = pyglet.graphics.Batch()
        self.bin = pyglet.image.atlas.TextureBin()
        self.frame_rate = pyglet.clock.ClockDisplay()

        self.community_layers = {
                'map': pyglet.graphics.OrderedGroup(0),
                'road': pyglet.graphics.OrderedGroup(1),
                'city': pyglet.graphics.OrderedGroup(2),
                'army': pyglet.graphics.OrderedGroup(3) }
    
        self.community_icons = {
                'city': self.load_icon('images/city-icon.png'),
                'army': self.load_icon('images/army-icon.png') }

        self.normal_shapes = self.load_team_icon('images/normal-shape.png')
        self.battle_shapes = self.load_team_icon('images/battle-shape.png')

        self.normal_outlines = self.load_team_icon('images/normal-selection.png')
        self.battle_outlines = self.load_team_icon('images/battle-selection.png')

        self.health_bar = self.load_health_icon('images/full-health.png', 25)
        self.health_outline = self.load_icon('images/empty-health.png')

    def get_name(self):
        return 'gui'

    def get_world(self):
        return self.world


    def setup(self):
        pass

    def update(self, time):
        pass

    def teardown(self):
        pass


    def on_draw(self):
        self.window.clear()
        pyglet.gl.glClearColor(255, 250, 240, 255)
        self.batch.draw()

    def on_mouse_release(self, x, y, button, modifiers):
        with self.lock():
            position = kxg.geometry.Vector(x, y)
            closest_distance = kxg.geometry.infinity
            closest_community = None

            for community in self.world.yield_communities():
                distance = position.get_distance(community.position)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_community = community

            if button == pyglet.window.mouse.LEFT:
                if closest_distance < 40:
                    if self.selection:
                        self.selection.get_extension().unselect()
                    self.selection = closest_community
                    self.selection.get_extension().select()

            if button == pyglet.window.mouse.RIGHT:
                message = messages.CreateArmy(self.player, position)
                self.send_message(message)

    def on_key_release(self, symbol, modifiers):
        with self.lock():
            pass


    def path_to_array(self, path):
        from matplotlib.pyplot import imread
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

        for name in colors:
            red, green, blue = colors[name]
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


    def start_game(self):
        pass

    def game_over(self, winner):
        pass

    def create_player(self, player, is_mine):
        if is_mine: self.player = player

    def create_city(self, city, is_mine):
        pass

    def create_army(self, army, is_mine):
        pass

    def create_road(self, road, is_mine):
        pass

    def upgrade_city(self, city, is_mine):
        pass

    def upgrade_army(self, city, is_mine):
        pass

    def move_army(self, army, target, is_mine):
        pass

    def attack_city(self, siege, was_me):
        pass

    def defend_city(self, siege, was_me):
        pass

    def capture_city(self, siege):
        pass

    def defeat_player(self, player):
        pass



class PlayerExtension (kxg.TokenExtension):

    def __init__(self, gui, player):
        self.gui = gui
        self.player = player
        self.wealth_label = None


    def setup(self):
        pass

    def update_wealth(self):

        player = self.player
        if not self.wealth_label:
            gui = self.gui
            if player is gui.player:
                window = gui.window
                batch = gui.batch
                #front = pyglet.graphics.OrderedGroup(1, parent=layer)

                self.wealth_label = pyglet.text.Label(
                        font_name='Deja Vu Sans', font_size=12,
                        color=(0, 0, 0, 255),
                        x=0, y=window.height,
                        anchor_x='left', anchor_y='top',
                        batch=batch)
            else:
                return

        wealth = player.wealth
        revenue = player.revenue
        self.wealth_label.text = '%4i + %3i' %(player.wealth, player.revenue)


    def teardown(self):
        self.wealth_label.delete()



class CommunityExtension (kxg.TokenExtension):

    def __init__(self, gui, token):
        self.gui = gui
        self.token = token

        batch = gui.batch
        layer = gui.community_layers[self.type]
        back = pyglet.graphics.OrderedGroup(0, parent=layer)
        front = pyglet.graphics.OrderedGroup(1, parent=layer)

        self.type_sprite = pyglet.sprite.Sprite(
                gui.community_icons[self.type],
                batch=batch, group=front)

        self.engagement_sprite = pyglet.sprite.Sprite(
                gui.normal_shapes[token.player.color],
                batch=batch, group=back)

        self.selection_sprite = pyglet.sprite.Sprite(
                gui.normal_outlines[token.player.color],
                batch=batch, group=back)

        self.health_bar_sprite = pyglet.sprite.Sprite(
                gui.health_bar[-1],
                batch=batch, group=front)

        self.health_outline_sprite = pyglet.sprite.Sprite(
                gui.health_outline,
                batch=batch, group=front)

        self.level_sprite = pyglet.text.Label(
                str(token.level),
                font_name='Deja Vu Sans Bold', font_size=14,
                color=(255, 255, 255, 255),
                anchor_x='center', anchor_y='center',
                batch=batch, group=front)

        self.selection_sprite.visible = False
        self.update_position()


    def setup(self):
        pass

    def update_position(self):
        vector = self.token.position - (40, 40)
        position = x, y = vector.tuple

        self.type_sprite.position = position
        self.engagement_sprite.position = position
        self.selection_sprite.position = position
        self.health_bar_sprite.position = position
        self.health_outline_sprite.position = position
        self.level_sprite.x = x + 40
        self.level_sprite.y = y + 50.25

    def update_health(self):
        frames = self.manager.health_bar

        health = self.token.get_health()
        max_health = self.token.get_max_health()
        max_index = len(frames) - 1
        index = (max_index * health) // max_health

        self.health_bar_sprite.image = frames[index]

    def update_level(self):
        level = self.token.get_level()
        self.level_sprite.text = str(level)

    def update_engagement(self):
        color = self.token.player.color

        if self.token.is_in_battle():
            self.engagement_sprite.image = self.gui.normal_shapes[color]
            self.selection_sprite.image = self.gui.normal_outlines[color]

        else:
            self.engagement_sprite.image = self.gui.battle_shapes[color]
            self.selection_sprite.image = self.gui.battle_outlines[color]

    def teardown(self):
        self.type_sprite.delete()
        self.engagement_sprite.delete()
        self.selection_sprite.delete()
        self.health_bar_sprite.delete()
        self.health_outline_sprite.delete()
        self.level_sprite.delete()


    def select(self):
        self.selection_sprite.visible = True

    def unselect(self):
        self.selection_sprite.visible = False


class CityExtension (CommunityExtension):
    type = 'city'

class ArmyExtension (CommunityExtension):
    type = 'army'



