#!/usr/bin/env python
# encoding: utf-8

# Imports (fold)
from __future__ import division

import kxg
import messages
import drawing
import arguments

import math
import numpy
import pyglet
import operator

#from pyglet.gl import *


class Gui (kxg.Actor):

    def __init__(self, window):
        kxg.Actor.__init__(self)

        self.player = None
        self.selection = None
        self.mode = None

        self.window = window

        self.drag_start_city = None
        self.play_again = False
        self.finished = False
        
        self.layers = {
                'map 1':        pyglet.graphics.OrderedGroup(0),
                'map 2':        pyglet.graphics.OrderedGroup(1),
                'road':         pyglet.graphics.OrderedGroup(2),
                'city':         pyglet.graphics.OrderedGroup(3),
                'capitol':      pyglet.graphics.OrderedGroup(3),
                'army':         pyglet.graphics.OrderedGroup(4),
                'gui':          pyglet.graphics.OrderedGroup(5),
                'messages 1':   pyglet.graphics.OrderedGroup(6),
                'messages 2':   pyglet.graphics.OrderedGroup(7) }

        self.status_area = None
        self.frame_rate = pyglet.clock.ClockDisplay()
    

    def get_name(self):
        return 'gui'

    def get_world(self):
        return self.world

    def postgame_finished(self):
        return self.finished


    def setup(self):
        self.player = None
        self.selection = None
        self.mode = None
        self.drag_start_city = None

        self.finished = False
        self.play_again = False

        self.bin = pyglet.image.atlas.TextureBin()

        gl = pyglet.gl
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA) 
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_DONT_CARE)

        self.community_icons = {
                'army': self.load_icon('images/army-icon.png'),
                'city': self.load_icon('images/city-icon.png'),
                'capitol': self.load_icon('images/capitol-icon.png') }

        self.normal_shapes = self.load_team_icon('images/normal-shape.png')
        self.campaign_shapes = self.load_team_icon('images/campaign-shape.png')
        self.battle_shapes = self.load_team_icon('images/battle-shape.png')

        self.normal_outlines = self.load_team_icon('images/normal-selection.png')
        self.battle_outlines = self.load_team_icon('images/battle-selection.png')

        self.normal_targets = self.load_team_icon('images/normal-waypoint.png')
        self.battle_targets = self.load_team_icon('images/battle-waypoint.png')

        self.health_bar = self.load_health_icon('images/full-health.png', 50)
        self.health_outline = self.load_icon('images/empty-health.png')

    def setup_pregame(self):
        width, height = self.window.get_size()

        self.batch = pyglet.graphics.Batch()
        self.stencil_batch = pyglet.graphics.Batch()

        group = self.layers['messages 2']
        self.pregame_message = pyglet.text.Label(
                "Waiting for players...", color=(255, 255, 255, 255),
                font_name='Deja Vu Sans', font_size=42,
                x=width//2, y=height//2,
                anchor_x='center', anchor_y='center',
                batch=self.batch, group=group)

        handlers = PregameHandlers(self)
        self.window.push_handlers(handlers)

    def setup_game(self):
        self.teardown_pregame()

        width, height = self.world.map.size
        handlers = GameHandlers(self)

        self.window.set_size(width, height)
        self.window.set_visible(True)
        self.window.push_handlers(handlers)

        self.mode_sprite = pyglet.text.Label("",
                font_name='Deja Vu Sans', font_size=12,
                x=(width / 2), y=5, color=(0, 0, 0, 255),
                anchor_x='center', anchor_y='bottom',
                batch=self.batch, group=self.layers['gui'])

        self.status_area = StatusArea(self)

    def setup_postgame(self):
        # Turn off any user input.
        handlers = PostgameHandlers(self)
        self.window.push_handlers(handlers)

        if self.selection:
            self.selection.get_extension().unselect()

        # Draw a transparent back rectangle across the screen.
        batch = self.batch
        group = self.layers['messages 1']

        window_width, window_height = self.window.get_size()
        banner_height = 100

        left, right = 0, window_width
        top = (window_height + banner_height) / 2
        bottom = (window_height - banner_height) / 2

        vertices = left, top, right, top, right, bottom, left, bottom
        color = 0, 0, 0, 0.8

        self.banner_background = batch.add(
                4, pyglet.gl.GL_QUADS, group,
                ('v2f', vertices),
                ('c4f', 4 * color))

        # Draw a victory or defeat message, as appropriate.
        if self.player is self.world.winner:
            message = "You won!"
        else:
            message = "You lost!"

        group = self.layers['messages 2']
        self.banner_message = pyglet.text.Label(
                message, color=(255, 255, 255, 255),
                font_name='Deja Vu Sans', font_size=42,
                x=window_width//2, y=window_height//2,
                anchor_x='center', anchor_y='center',
                batch=batch, group=group)

        # Draw a "Play again?" message.
        self.play_again_message = pyglet.text.Label(
                "Enter: Play Again\nEsc: Quit Game", color=(0, 0, 0, 255),
                font_name='Deja Vu Sans', font_size=12,
                x=(window_width - 8), y=(window_height - 5),
                anchor_x='right', anchor_y='top',
                multiline=True, width=200,
                batch=batch, group=group)

        self.play_again_message.set_style('align', 'right')
        


    def update(self, time):
        if self.status_area:
            self.status_area.update(time)

    def update_mode(self, mode=None):
        self.mode = mode
        self.status_area.change_mode()

    def update_selection(self, community=None):
        if self.selection:
            self.selection.get_extension().unselect()
        self.selection = community
        if self.selection:
            self.selection.get_extension().select()

    def update_background(self):
        if not self.player:
            pyglet.gl.glClearColor(0, 0, 0, 1)
            return

        player_color = colors[self.player.color]
        player_color = fade_color(player_color, 0.85) + (1,)
        background_color = [x / 255 for x in colors['background']] + [1]

        if self.player in self.world.losers:
            pyglet.gl.glClearColor(*background_color)
        elif not self.player.cities:
            pyglet.gl.glClearColor(*player_color)
        else:
            pyglet.gl.glClearColor(*background_color)


    def teardown_pregame(self):
        self.pregame_message.delete()
        self.window.pop_handlers()

    def teardown(self):
        self.window.pop_handlers()

    def teardown_postgame(self):
        self.banner_message.delete()
        self.banner_background.delete()
        self.play_again_message.delete()

        self.window.pop_handlers()


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
        self.setup_game()

    def game_over(self, winner):
        pass

    def create_player(self, player, is_mine):
        if is_mine: self.player = player

    def create_city(self, city, is_mine):
        # This is a hack for the first city.  The first city gets created 
        # before self.player is set, so update_engagement() doesn't work like 
        # it should.  There's probably a better way to address this, but it 
        # probably involves tweaking the game engine.
        city.get_extension().update_engagement()

    def create_army(self, army, is_mine):
        pass

    def create_road(self, road, is_mine):
        pass

    def upgrade_community(self, community, is_mine):
        pass

    def destroy_army(self, army, is_mine):
        if self.selection is army:
            self.update_selection()

    def request_battle(self, campaign, is_mine):
        pass

    def start_battle(self, battle):
        pass

    def join_battle(self, battle):
        pass

    def retreat_battle(self, army, is_mine):
        pass

    def zombify_city(self, battle, city, is_mine):
        pass

    def end_battle(self, battle, is_mine):
        if self.selection is battle.get_zombie_city():
            self.update_selection()

    def move_army(self, army, target, is_mine):
        pass

    def attack_city(self, battle, is_mine):
        pass

    def defend_city(self, battle, is_mine):
        pass

    def defeat_player(self):
        pass

    
    def show_error(self, message):
        self.status_area.add_warning(message.error)



colors = {            # (fold)
        'red':          (164,   0,   0),
        'brown':        (143,  89,   2),
        'orange':       (206,  92,   0),
        'yellow':       (196, 160,   0),
        'green':        ( 78, 154,   6),
        'blue':         ( 32,  74, 135),
        'purple':       ( 92,  53, 102),
        'black':        ( 46,  52,  54),
        'background':   (255, 250, 240),
}

def fade_color(source, extent=0.80):
    r = interpolate_color(source[0], 255, extent) / 255
    g = interpolate_color(source[1], 255, extent) / 255
    b = interpolate_color(source[2], 255, extent) / 255
    return (r, g, b)

def interpolate_color(start, end, extent):
    return start + extent * (end - start)


class BaseHandlers (object):

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
        with self.gui.lock():
            position = kxg.geometry.Vector(x, y)
            find_closest_community = self.gui.player.find_closest_community
            
            if button == pyglet.window.mouse.LEFT:
                if self.gui.mode == 'develop':
                    drag_start = find_closest_community(position, cutoff=40)
                    if drag_start and drag_start.is_city():
                        self.gui.drag_start_city = drag_start

            if button == pyglet.window.mouse.MIDDLE:
                print 'Players:', self.gui.world.players
                print
                for player in self.gui.world.players:
                    print ' %s:' % player.name
                    print ' Cities:', player.cities
                    print ' Armies:', player.armies
                print

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        with self.gui.lock():
            position = kxg.geometry.Vector(x, y)
            
            if button == pyglet.window.mouse.LEFT:
                drag_start = self.gui.drag_start_city
                if drag_start:
                    drag_dist = position.get_distance(drag_start.position)
                    if self.gui.mode == 'develop' and drag_dist > 40:
                        self.gui.update_mode('develop road')
                    elif self.gui.mode == 'develop road' and drag_dist <= 40:
                        self.gui.update_mode('develop')

    def on_mouse_release(self, x, y, button, modifiers):
        with self.gui.lock():
            position = kxg.geometry.Vector(x, y)
            find_closest_community = self.gui.player.find_closest_community
            
            if button == pyglet.window.mouse.LEFT:
                if self.gui.mode == 'fight':
                    message = messages.CreateArmy(self.gui.player, position)
                    self.gui.send_message(message)
                    self.gui.update_mode()
                    self.gui.update_selection()

                elif self.gui.mode == 'develop road':
                    drag_start = self.gui.drag_start_city
                    drag_end = self.gui.world.find_closest_community(position, cutoff=40)
                    self.gui.drag_start_city = None
                    
                    if drag_start and drag_end:
                        if drag_start.is_city() and drag_end.is_city():
                            if not (drag_start is drag_end):
                                message = messages.CreateRoad(self.gui.player, drag_start, drag_end)
                                self.gui.send_message(message)
                                self.gui.update_selection()
                    self.gui.update_mode()

                elif self.gui.mode == 'develop':
                    if self.gui.drag_start_city:
                        #upgrade?
                        self.gui.drag_start_city = None
                    else:
                        message = messages.CreateCity(self.gui.player, position)
                        self.gui.send_message(message)
                        self.gui.update_mode()
                    self.gui.update_selection()

                else:
                    community = find_closest_community(position, cutoff=40)
                    self.gui.update_selection(community)

            if button == pyglet.window.mouse.RIGHT:
                target = self.gui.world.find_closest_community(position, cutoff=40)
                if target and target.player is self.gui.player:
                    target = None

                if self.gui.selection and self.gui.selection.can_move():
                    if target:
                        if self.gui.selection.is_chasing():
                            campaign = self.gui.selection.get_campaign()
                            if campaign.get_community() is target:
                                # Trying to attack a community that the 
                                # army is already chasing. Just ignore 
                                # it.
                                pass
                            else:
                                # Cancel campaign
                                # Request battle
                                pass
                        else:
                            message = messages.RequestBattle(self.gui.selection, target)
                            self.gui.send_message(message)
                    else:
                        message = messages.MoveArmy(self.gui.selection, position)
                        self.gui.send_message(message)

    def on_key_press(self, symbol, modifiers):
        with self.gui.lock():
            if symbol == pyglet.window.key.F:
                self.gui.update_mode('fight')
            if symbol == pyglet.window.key.D:
                self.gui.update_mode('develop')
            if symbol == pyglet.window.key.SPACE and self.gui.selection:
                message = messages.UpgradeCommunity(self.gui.selection)
                self.gui.send_message(message)
            if symbol == pyglet.window.key.BACKSPACE and self.gui.selection:
                message = messages.RetreatBattle(self.gui.selection)
                self.gui.send_message(message)
            if symbol == pyglet.window.key.ESCAPE:
                self.gui.update_mode()
                return True


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



class PlayerExtension (kxg.TokenExtension):

    def __init__(self, gui, player):
        self.gui = gui
        self.player = player
        self.wealth_label = None
        self.cost_label = None

    def setup(self):
        pass

    def update_wealth(self):
        player = self.player
        wealth = player.wealth
        revenue = player.revenue

        if not self.wealth_label:
            gui = self.gui

            if player is gui.player:
                window = gui.window
                batch = gui.batch
                layer = gui.layers['gui']

                self.wealth_label = pyglet.text.Label(
                        font_name='Deja Vu Sans', font_size=12,
                        color=(0, 0, 0, 255), bold=True,
                        x=5, y=window.height - 5,
                        anchor_x='left', anchor_y='top',
                        batch=batch, group=layer)
            else:
                return

        self.wealth_label.text = '%d/%+d' % (wealth, revenue)

    def update_costs(self):
        player = self.player

        if not self.cost_label:
            gui = self.gui

            if player is gui.player:
                window = gui.window
                batch = gui.batch
                layer = gui.layers['gui']

                self.cost_label = pyglet.text.Label(
                        font_name='Deja Vu Sans', font_size=12,
                        color=(0, 0, 0, 255),
                        x=5, y=window.height - 24,
                        anchor_x='left', anchor_y='top',
                        multiline=True, width=200,
                        batch=batch, group=layer)
            else:
                return

        message  = 'Build City: %d\n' % player.get_city_price()
        message += 'Build Army: %d\n' % player.get_army_price()
        message += 'Build Road: %d\n' % player.get_road_price()

        selection = self.gui.selection
        if selection:
            if selection.is_city():
                message += 'Upgrade City: %d\n' % selection.get_upgrade_price()
            elif selection.is_army():
                message += 'Upgrade Army: %d\n' % selection.get_upgrade_price()
                message += 'Attack: %d\n' % selection.get_battle_price()
                message += 'Retreat: %d\n' % selection.get_retreat_price()

        self.cost_label.text = message

    def teardown(self):
        self.wealth_label.delete()


class CommunityExtension (kxg.TokenExtension):

    def __init__(self, gui, token):
        self.gui = gui
        self.token = token
        self.active = True

        batch = gui.batch
        layer = gui.layers[self.type]
        back = pyglet.graphics.OrderedGroup(0, parent=layer)
        front = pyglet.graphics.OrderedGroup(1, parent=layer)

        self.back = back
        self.front = front

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

        self.vision_sprite = None

        self.selection_sprite.visible = False
        self.update_position()


    def setup(self):
        pass

    def update(self, time):
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
        frames = self.gui.health_bar

        health = self.token.get_health()
        max_health = self.token.get_max_health()
        max_index = len(frames) - 1
        index = max_index * health / max_health
        self.health_bar_sprite.image = frames[int(index)]

    def update_level(self):
        level = self.token.get_level()
        self.level_sprite.text = str(level)

    def update_engagement(self):
        color = self.token.player.color

        if self.token.is_in_battle():
            self.engagement_sprite.image = self.gui.battle_shapes[color]
            self.selection_sprite.image = self.gui.battle_outlines[color]

        else:
            self.engagement_sprite.image = self.gui.normal_shapes[color]
            self.selection_sprite.image = self.gui.normal_outlines[color]

    def teardown(self):
        self.active = False
        self.type_sprite.delete()
        self.engagement_sprite.delete()
        self.selection_sprite.delete()
        self.health_bar_sprite.delete()
        self.health_outline_sprite.delete()
        self.level_sprite.delete()


    def select(self):
        self.selection_sprite.visible = True

    def unselect(self):
        if self.active:
            self.selection_sprite.visible = False


class ArmyExtension (CommunityExtension):
    type = 'army'

    def __init__(self, gui, token):
        CommunityExtension.__init__(self, gui, token)

        self.target_sprite = pyglet.sprite.Sprite(
                gui.normal_targets[token.player.color],
                batch=gui.batch, group=gui.layers['gui'])

        self.target_sprite.visible = False

    def update(self, time):
        position = self.token.position
        target = self.token.target

        if self.token.player is not self.gui.player:
            return

        if target:
            distance = position.get_distance(target)
            if distance < 30: self.hide_target()

    def update_target(self):
        if self.token.player is not self.gui.player:
            return

        position = self.token.target - (8, 8)
        self.target_sprite.visible = True
        self.target_sprite.position = position.tuple

    def update_engagement(self):
        color = self.token.player.color

        if self.token.is_in_battle():
            self.engagement_sprite.image = self.gui.battle_shapes[color]
            self.selection_sprite.image = self.gui.battle_outlines[color]

        elif self.token.is_chasing():
            self.engagement_sprite.image = self.gui.campaign_shapes[color]
            self.selection_sprite.image = self.gui.battle_outlines[color]

        else:
            self.engagement_sprite.image = self.gui.normal_shapes[color]
            self.selection_sprite.image = self.gui.normal_outlines[color]

    def hide_target(self):
        self.target_sprite.visible = False


class CityExtension (CommunityExtension):

    type = 'city'

    def __init__(self, gui, token):
        CommunityExtension.__init__(self, gui, token)
        self.inner_circle = None
        self.outer_circle = None

        self.update_capitol()
        self.update_engagement()

    def update_capitol(self):
        icon = 'capitol' if self.token.is_capitol() else 'city'

        self.type_sprite = pyglet.sprite.Sprite(
                self.gui.community_icons[icon],
                batch=self.gui.batch, group=self.front)

        self.update_position()

    def update_engagement(self):
        CommunityExtension.update_engagement(self)

        gui = self.gui
        token = self.token

        num_vertices = 50
        center = token.position
        vector = kxg.geometry.Vector.from_radians

        inner_vertices = ()
        outer_vertices = ()
        inner_radius = token.buffer
        outer_radius = token.border

        for iteration in range(num_vertices + 1):
            angle = math.pi * iteration / num_vertices
            if iteration % 2: angle *= -1

            inner_vertex = token.position + inner_radius * vector(angle)
            outer_vertex = token.position + outer_radius * vector(angle)
            inner_vertices += inner_vertex.tuple
            outer_vertices += outer_vertex.tuple

        inner_vertices = inner_vertices[0:2] + inner_vertices + inner_vertices[-2:]
        outer_vertices = outer_vertices[0:2] + outer_vertices + outer_vertices[-2:]

        player_color = colors[token.player.color]
        player_color = fade_color(player_color, 0.85)
        background_color = colors['background']

        if self.inner_circle: 
            self.inner_circle.delete()
            self.inner_circle = None
        if self.outer_circle:
            self.outer_circle.delete()
            self.outer_circle = None

        if token.player is gui.player:
            self.inner_circle = gui.batch.add(
                    num_vertices + 3,
                    pyglet.gl.GL_TRIANGLE_STRIP,
                    gui.layers['map 2'],
                    ('v2f', inner_vertices),
                    ('c3B', background_color * (num_vertices + 3)) )

            self.outer_circle = gui.batch.add(
                    num_vertices + 3,
                    pyglet.gl.GL_TRIANGLE_STRIP,
                    gui.layers['map 1'],
                    ('v2f', outer_vertices),
                    ('c3f', player_color * (num_vertices + 3)) )

        else:
            self.outer_circle = gui.batch.add(
                    num_vertices + 3,
                    pyglet.gl.GL_TRIANGLE_STRIP,
                    gui.layers['map 2'],
                    ('v2f', outer_vertices),
                    ('c3B', background_color * (num_vertices + 3)) )


class RoadExtension (kxg.TokenExtension):

    def __init__(self, gui, road):
        self.gui = gui
        self.road = road
        self.width = 1.5
        self.sprite = None

        self.update_owner()

    def update_owner(self):
        if self.sprite:
            self.sprite.delete()

        start, end = self.road.start.position, self.road.end.position
        stroke = self.width

        if self.road.is_blocked(): color = drawing.gray
        else: color = drawing.colors[self.road.player.color]

        batch = self.gui.batch
        group = self.gui.layers['road']

        self.sprite = drawing.draw_pretty_line(
                start, end, stroke, color=color, batch=batch, group=group)

    def setup(self):
        pass

    def teardown(self):
        self.sprite.delete()



class StatusArea (object):

    def __init__(self, gui):
        self.gui = gui
        self.warning = ""
        self.elapsed = 0

        width, height = self.gui.window.get_size()
        self.widget = pyglet.text.Label(
                "", color=(0, 0, 0, 255),
                font_name='Deja Vu Sans', font_size=12,
                x=width//2, y=5,
                anchor_x='center', anchor_y='bottom',
                batch=self.gui.batch, group=self.gui.layers['messages 2'])

    def change_mode(self):
        if self.gui.mode == 'develop':
            mode = "Click to place a city."
        elif self.gui.mode == 'fight':
            mode = "Click to place an army."
        elif self.gui.mode == 'develop road':
            mode = "Drag to another city to place a road."
        else:
            mode = ""

        self.widget.text = mode
        self.warning = False

    def add_warning(self, message):
        self.widget.text = message
        self.warning = True
        self.elapsed = 0

    def update(self, time):

        if self.warning:
            self.elapsed += time
            if self.elapsed > 2:
                self.change_mode()

