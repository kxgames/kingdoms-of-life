from __future__ import division

import pygame
from pygame.locals import *

import kxg
import messages

class Hotkeys:

    def __init__ (self, gui):
        self.keychain = kxg.gui.Keychain()
        self.event = None
        self.gui = gui
        
        self.click_drag = False
        self.start_click = None
        self.end_click = None

    def __str__ (self):
        return 'Keychain Manager'

    def __repr__ (self):
        return self.__str__()

    def setup (self):
        self.keychain.verbose = False
        self.keychain.setup()

        self.setup_hotkeys()
        self.setup_lenses()

    def setup_lenses (self):
        ## Register lenses

        k2s = kxg.gui.key_to_string
        e2s = kxg.gui.event_to_string

        # Make the "d" lens
        d_lens = {
                e2s[ MOUSEMOTION ]      : "dMOUSEMOTION",
                e2s[ MOUSEBUTTONUP ]    : "dMOUSEBUTTONUP",
                e2s[ MOUSEBUTTONDOWN ]  : "dMOUSEBUTTONDOWN"
                }

        f_lens = {
                e2s[ MOUSEBUTTONUP ]    : "fMOUSEUP",
                e2s[ MOUSEBUTTONDOWN ]  : "fMOUSEDOWN"
                }
        
        self.keychain.register_lens (k2s[ K_d ], d_lens)
        self.keychain.register_lens (k2s[ K_f ], f_lens)

    def setup_hotkeys (self):

        ## Register keyboard hotkeys
        register_keys = self.keychain.register_chain_key

        # Special sequences.
        register_keys ([K_q], self.exit, None)
        register_keys ([K_SPACE],  self.info, None)

        ## Register mouse hotkeys
        left = kxg.gui.mouse_to_string[1]

        d_sequence = ["dMOUSEBUTTONDOWN", left]
        register_chain (d_sequence, self.develop_init, None)

        d_sequence += ["dMOUSEMOTION"]
        register_chain (d_sequence, self.develop_motion, None)

        d_sequence += ["dMOUSEBUTTONUP", left]
        register_chain (d_sequence, self.develop, None)

        register_chain (["fMOUSEDOWN", left], self.fuck, None)

    def handle (self, event):
        self.event = event

        if event.type == KEYDOWN:
            self.keychain.handle_key (event.key)

        elif event.type == KEYUP:
            self.keychain.handle_key (event.key, True)

        elif event.type == MOUSEBUTTONDOWN:
            self.keychain.handle_event(event.type)
            self.keychain.handle_mouse(event.button)

        else:
            pass


    # Callbacks

    def exit (self, args):
        #self.gui.postgame_finished = True
        raise SystemExit

    def develop_init (self, args):
        self.click_drag = False
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.start_click = position

    def develop_motion (self, args):
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.end_click = position

        min = Gui.minimum_drag_distance
        click_dist = (position - self.start_click).magnitude_squared
        self.click_drag = (click_dist >= min**2)? True : False

    def develop (self, args):
        player = self.gui.player
        start_click = self.start_click
        end_click = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.end_click = end_click

        if self.click_drag:
            # Build road
            self.click_drag = False

            start_city = (kxg.geometry.infinity, None)
            end_city = (kxg.geometry.infinity, None)
            cities = self.gui.world.cities
            for city in cities:
                city_position = city.position
                dist = (start_click - city_position).magnitude_squared

                if dist < start_city[0]:
                    start_city = (dist, city)

            for city in cities:
                city_position = city.position
                dist = (end_click - city_position).magnitude_squared

                if dist < end_city[0] and not city == start_city[1]:
                    end_city = (dist, city)

            if not start_city[1] == None and not end_city[1] == None:
                start = start_city[1]
                end = end_city[1]
                message = messages.CreateRoad(player, start, end)
                self.gui.send_message(message)
        else:
            # Build city
            message = messages.CreateCity(player, position)
            self.gui.send_message(message)

    def fuck (self, args):
        pass 

    def info (self, args):
        pass


class Gui (kxg.Actor):

    background = "Black"
    city_outline = "Black"
    city_color = "White"
    city_text = "Black"
    city_radius = 30

    minimum_drag_distance = 7

    def __init__(self):
        kxg.Actor.__init__(self)

        self.world = None
        self.player = None

        self.size = None
        self.hotkeys = Hotkeys(self)

        self.postgame_finished = False

    def get_name(self):
        return 'gui'

    def get_world(self):
        return self.world


    def setup(self, world):
        self.world = world
        self.hotkeys.setup()

    def update(self, time):
        if not self.world.has_game_started():
            return

        elif not self.world.has_game_ended():
            self.timer += time

            if self.timer > self.timeout:
                self.timer -= self.timeout
                self.soft_refresh = True

            if self.soft_refresh or self.hard_refresh:
                self.draw(time)
                self.soft_refresh = False

            self.react(time)

        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.postgame_finished = True

    def create_player(self, player, is_mine):
        if is_mine: self.player = player

    def start_game(self):
        pygame.init()

        self.size = self.world.map.size.pygame

        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(gui.background_color)

        self.big_font = pygame.font.Font(None, 50)
        self.status_font = pygame.font.Font(None, 20)

        self.timer = 0
        self.timeout = gui.gui_refresh_rate

        self.soft_refresh = True
        self.hard_refresh = True

    def place_city(self, city):
        self.refresh()

    def place_road(self, road):
        self.refresh()

    def teardown(self):
        pass

    def is_finished(self):
        return self.postgame_finished


    def draw(self, time):

        if self.hard_refresh:
            self.screen.fill(Gui.background)
            self.draw_roads(self.screen)
            self.draw_cities(self.screen)

            self.hard_refresh = False

        self.draw_player(self.screen)
        #self.draw_hotkey_bar(self.screen)

        pygame.display.flip()

    def draw_player(self, screen):

        status = "Wealth: %d" % (self.player.wealth)

        color = gui.text_color
        text = self.status_font.render(status, True, color)

        dimensions = text.get_size()

        map_size = self.world.get_map_size()
        text_position = 5, map_size.get_y() - dimensions[1]

        screen.blit(text, text_position)

    def draw_roads (self, screen):
        roads = self.world.roads

        color = self.player.color

        for road in roads:
            start = road.start.position
            end = road.end.position

            pygame.draw.aaline(screen, color, start.pygame, end.pygame)

    def draw_cities (self, screen):
        cities = self.world.cities

        color = Gui.city_color
        outline = self.player.color

        text_color = Gui.city_text
        from_tuple = kxg.geometry.Vector.from_tuple

        for city in cities:
            position = city.position

            pygame.draw.circle(screen, color, position.pygame, radius, outline)

            level = "%d" %city.level
            text_surface = self.status_font.render(level, True, text_color)

            text_size = from_tuple (text_surface.get_size())
            text_position = position - text_size / 2

            screen.blit(text_surface, text_position.pygame)

    def draw_hotkey_bar(self, screen):

        width, height = self.size[0], gui.hotkey_height
        top, left = self.size[1] - height, 0

        color = gui.hotkey_background_color
        padding = gui.hotkey_padding

        rectangle = Rect(left, top, width, height)
        pygame.draw.rect(screen, color, rectangle)

        text_surface = gui.hotkey_message
        text_height = text_surface.get_height()

        screen.blit(text_surface, (left + padding, top + padding))

    def refresh(self):
        self.hard_refresh = True

    def react(self, time):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.postgame_finished = True
            self.hotkeys.handle(event)

