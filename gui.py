from __future__ import division

import pygame
from pygame.locals import *

import kxg
import messages

Color = pygame.color.Color
Font = pygame.font.Font
Image = pygame.image.load

pygame.font.init()

class Hotkeys:

    def __init__ (self, gui):
        self.keychain = kxg.gui.Keychain()
        self.event = None
        self.gui = gui

    def __str__ (self):
        return "Keychain Manager"

    def setup (self):
        self.keychain.verbose = False
        self.keychain.setup()

        self.setup_hotkeys()
        self.setup_lenses()

    def setup_lenses (self):
        ## Register lenses

        k2s = kxg.gui.key_to_string
        e2s = kxg.gui.event_to_string

        # Make the 'd' lens
        d_lens = {
                e2s[MOUSEMOTION]      : 'dMOUSEMOTION',
                e2s[MOUSEBUTTONUP]    : 'dMOUSEBUTTONUP',
                e2s[MOUSEBUTTONDOWN ] : 'dMOUSEBUTTONDOWN' }

        f_lens = {
                e2s[MOUSEBUTTONUP]    : 'fMOUSEUP',
                e2s[MOUSEBUTTONDOWN]  : 'fMOUSEDOWN' }
        
        self.keychain.register_lens (k2s[ K_d ], d_lens)
        self.keychain.register_lens (k2s[ K_f ], f_lens)

    def setup_hotkeys (self):

        ## Register keyboard hotkeys
        register_keys = self.keychain.register_chain_key
        register_chain = self.keychain.register_chain

        # Special sequences.
        register_keys ([K_q], self.exit, None)
        register_keys ([K_SPACE],  self.info, None)

        ## Register mouse hotkeys
        left = kxg.gui.mouse_to_string[1]

        d_sequence = ['dMOUSEBUTTONDOWN', left]
        register_chain (d_sequence, self.develop_init, None)

        d_sequence += ['dMOUSEMOTION']
        register_chain (d_sequence, self.develop_motion, None)

        d_sequence += ['dMOUSEBUTTONUP', left]
        register_chain (d_sequence, self.develop, None)

        register_chain (['fMOUSEDOWN', left], self.fuck, None)

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

    def develop_init(self, args):
        pass

    def develop_motion(self, args):
        pass

    def develop(self, args):
        pass

    def fuck(self, args):
        pass
    

    def exit (self, args):
        #self.gui.postgame_finished = True
        raise SystemExit

    def build (self, args):
        gui = self.gui
        city = gui.selected_city

        if city is not None:
            type, subtype = args[0], args[1]
            message = messages.PlaceBuilding(city, type, subtype)
            gui.send_message(message)

        else:
            print "No city selected."

    def cycle (self, args):
        self.gui.hard_refresh = True
        cities = self.gui.get_world().get_cities()

        for city in cities:
            small_menu = city.get_small_menu()
            small_menu.toggle()

    def info (self, args):
        gui = self.gui
        world = gui.get_world()

        print '\nInfo'

        # Display info in the terminal.
        if gui.selected_city == None:
            cities = world.get_cities()
            for city in cities:
                gui.print_city_data(city)
        else:
            gui.print_city_data(gui.selected_city)

    def left_click (self, args):
        gui = self.gui
        world = gui.get_world()
        position = kxg.geometry.Vector.from_tuple(self.event.pos)

        if gui.active_menu and                         \
                gui.active_menu.under_mouse(position):
            gui.selected_resource =                    \
                    gui.active_menu.select_resource(position)
            gui.refresh()

        else:
            gui.selected_city = world.find_city(position)
            if gui.selected_city:
                gui.active_menu = gui.selected_city.get_large_menu()
            gui.refresh()

    def middle_click (self, args):
        pass

    def right_click (self, args):
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        message = messages.PlaceCity(position)
        self.gui.send_message(message)


class Gui (kxg.Actor):

    background = 'white'
    text_color = 'black'
    city_radius = 30
    city_font = Font(None, 20)
    status_font = Font(None, 16)
    refresh_rate = 0.2

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

        self.size = self.world.map.size
        self.screen = pygame.display.set_mode(self.size)

        self.timer = 0
        self.timeout = self.refresh_rate

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
            self.hard_refresh = False
            self.clear()
            self.draw_roads(self.screen)
            self.draw_cities(self.screen)

        self.draw_player(self.screen)

        pygame.display.flip()

    def clear(self):
        color = Color(self.background)
        self.screen.fill(color)

    def draw_player(self, screen):
        status = "Wealth: %d" % self.player.wealth
        color = Color(self.text_color)
        background = Color(self.background)
        text = self.status_font.render(status, True, color)

        rect = kxg.geometry.Rectangle.from_surface(text).pygame
        pygame.draw.rect(screen, background, rect)

        position = 5, 5
        screen.blit(text, position)

    def draw_roads (self, screen):
        for player in self.world.players:
            for road in player.roads:
                start = road.start.position.pygame
                end = road.end.position.pygame

                pygame.draw.aaline(screen, player.color, start, end)

    def draw_cities (self, screen):
        text_color = Color(self.text_color)
        fill_color = Color(self.background)
        rect_from_surface = kxg.geometry.Rectangle.from_surface

        for player in self.world.players:
            for city in player.cities:
                position = city.position
                city_level = "%d" % city.level
                player_color = Color(player.color)

                pygame.draw.circle(
                        screen, fill_color, position.pygame, radius)
                pygame.draw.circle(
                        screen, outline_color, position.pygame, radius, 1)

                text_surface = self.city_font.render(
                        city_level, True, text_color)
                text_rect = rect_from_surface(text_surface)
                text_position = position - text_rect.center

                screen.blit(text_surface, text_position.pygame)


    def refresh(self):
        self.hard_refresh = True

    def react(self, time):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.postgame_finished = True
            self.hotkeys.handle(event)

