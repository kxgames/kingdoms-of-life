#!/usr/bin/env python

from __future__ import division

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

        self.window = window
        self.window.set_handler(self)
        self.batch = pyglet.graphics.Batch()
        self.bin = pyglet.image.atlas.TextureBin()
    
        self.map_layer = pyglet.graphics.OrderedGroup(0)
        self.road_layer = pyglet.graphics.OrderedGroup(1)
        self.city_layer = pyglet.graphics.OrderedGroup(2)
        self.army_layer = pyglet.graphics.OrderedGroup(3)
    
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
        pyglet.gl.glClearColor(255, 250, 240, 255)
        self.batch.draw()

    def on_mouse_release(self, x, y, button, modifiers):

    # Community placement
    if modifiers & pyglet.window.key.MOD_CTRL:
        if closest_distance < 100:
            return

        if button == pyglet.window.mouse.LEFT:
            city = CityIcon(manager, x, y, color)
            communities.append(city)

        if button == pyglet.window.mouse.RIGHT:
            army = ArmyIcon(manager, x, y, color)
            communities.append(army)

    # Selection and movement
    else:
        global selection

        if button == pyglet.window.mouse.LEFT:
            if closest_distance < 40:
                if selection: selection.unselect()
                selection = closest_community
                selection.select()
            else:
                if selection: selection.unselect()
                selection = None

        if selection and button == pyglet.window.mouse.RIGHT:
            selection.target = x, y


    def on_key_release(self, symbol, modifiers):
        pass


    def path_to_array(self, path):
        buffer = 255 * imread(path)
        buffer = buffer.astype('uint8')
        return buffer

    def array_to_texture(self, buffer):
        width, height = buffer.shape[0:2]
        data, stride = buffer.tostring(), -buffer.strides[0]
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



class CommunityExtension (kxg.TokenExtension):

    def __init__(self, gui, token):
        self.gui = gui
        self.token = token

        batch = gui.batch
        layer = self.get_layer()
        back = pyglet.graphics.OrderedGroup(0, parent=layer)
        front = pyglet.graphics.OrderedGroup(1, parent=layer)

        self.type_sprite = pyglet.sprite.Sprite(
                gui.community_types[self.type],
                x=x, y=y, batch=batch, group=front)

        self.engagement_sprite = pyglet.sprite.Sprite(
                gui.normal_shapes[color],
                x=x, y=y, batch=batch, group=back)

        self.selection_sprite = pyglet.sprite.Sprite(
                gui.normal_outlines[color],
                x=x, y=y, batch=batch, group=back)

        self.health_bar_sprite = pyglet.sprite.Sprite(
                gui.health_bar[-1],
                x=x, y=y, batch=batch, group=front)

        self.health_outline_sprite = pyglet.sprite.Sprite(
                gui.health_outline,
                x=x, y=y, batch=batch, group=front)

        self.level_sprite = pyglet.text.Label(
                str(token.level),
                font_name='Deja Vu Sans Bold', font_size=14,
                x=(x + 40), y=(y + 50.25), color=(255, 255, 255, 255),
                anchor_x='center', anchor_y='center',
                group=front, batch=batch)

        self.selection_sprite.visible = False


    def setup(self):
        pass

    def update_position(self):
        position = x, y = self.token.position.tuple

        self.type_sprite.position = position
        self.engagement_sprite.position = position
        self.selection_sprite.position = position
        self.health_bar_sprite.position = position
        self.health_outline_sprite.position = position
        self.level_sprite.position = x + 40, y + 50.25

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
        color = self.token.get_player.get_color()

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
        self.outline.visible = True

    def unselect(self):
        self.outline.visible = False


class CityExtension (CommunityExtension):
    type = 'city'

class ArmyExtension (CommunityExtension):
    type = 'army'



#!/usr/bin/env python

from __future__ import division

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

        self.window = window
        self.window.set_handler(self)
        self.batch = pyglet.graphics.Batch()
        self.bin = pyglet.image.atlas.TextureBin()
    
        self.map_layer = pyglet.graphics.OrderedGroup(0)
        self.road_layer = pyglet.graphics.OrderedGroup(1)
        self.city_layer = pyglet.graphics.OrderedGroup(2)
        self.army_layer = pyglet.graphics.OrderedGroup(3)
    
        self.community_icons = {
                'city': self.load_icon('images/city-icon.png'),
                'army': self.load_icon('images/army-icon.png') }

        self.normal_shapes = self.load_team_icon('images/normal-shape.png')
        self.battle_shapes = self.load_team_icon('images/battle-shape.png')
