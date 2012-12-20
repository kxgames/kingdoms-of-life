from __future__ import division

import pygame
from pygame.locals import *

import kxg
import messages
import random

Color = pygame.color.Color
Font = pygame.font.Font
Image = pygame.image.load

pygame.font.init()

class Hotkeys:

    def __init__ (self, gui):
        self.keychain = kxg.gui.Keychain()
        self.event = None
        self.gui = gui
        
        self.click_drag = False
        self.start_click = None
        self.end_click = None

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

        #alt = { k2s[ K_BACKSPACE ] : k2s[ K_BACKSPACE ] }
        alt = { }
        
        self.keychain.register_lens (k2s[ K_LALT ], alt)
        self.keychain.register_lens (k2s[ K_d ], d_lens)
        self.keychain.register_lens (k2s[ K_f ], f_lens)

    def setup_hotkeys (self):

        ## Register keyboard hotkeys
        register_keys = self.keychain.register_chain_key
        register_chain = self.keychain.register_chain

        # Special sequences.
        register_keys ([K_SPACE],  self.info, None)

        ## Register mouse hotkeys
        left = kxg.gui.mouse_to_string[1]

        develop_init = ['dMOUSEBUTTONDOWN', left]
        register_chain (develop_init, self.develop_init, None)

        develop_motion = ['dMOUSEBUTTONDOWN', left, 'dMOUSEMOTION']
        register_chain (develop_motion, self.develop_motion, None)

        develop = ['dMOUSEBUTTONDOWN', left, 'dMOUSEBUTTONUP', left]
        register_chain (develop, self.develop, None)

        develop = ['dMOUSEBUTTONDOWN', left, 'dMOUSEMOTION', 'dMOUSEBUTTONUP', left]
        register_chain (develop, self.develop, None)

        register_chain (['fMOUSEDOWN', left], self.fuck, None)

    def handle (self, event):
        self.event = event

        if event.type == KEYDOWN:
            self.keychain.handle_key (event.key)

        elif event.type == KEYUP:
            self.keychain.handle_key (event.key, True)

        #elif event.type == MOUSEMOTION:
        #    self.keychain.handle_event(event.type)

        elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            self.keychain.handle_event(event.type)
            self.keychain.handle_mouse(event.button)

        else:
            pass


    # Callbacks

    def develop_init (self, args):
        self.click_drag = False
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.start_click = position

    def develop_motion (self, args):
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.end_click = position

        min = Gui.minimum_drag_distance
        click_dist = (position - self.start_click).magnitude_squared
        self.click_drag = click_dist >= min**2

    def develop (self, args):
        player = self.gui.player

        start_click = self.start_click
        end_click = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.end_click = end_click

        drag_vector = end_click - self.start_click
        drag_distance = drag_vector.magnitude

        # If the actual drag distance exceeds the minimum drag threshold, then 
        # build a road.  This requires finding the two cities nearest the 
        # end-points of the drag event.

        if drag_distance >= self.gui.minimum_drag_distance:
            self.click_drag = False

            start_city = self.find_closest_city(start_click, 'mine')
            end_city = self.find_closest_city(end_click, 'mine')

            if start_city is not None and end_city is not None:
                message = messages.CreateRoad(player, start_city, end_city)
                self.gui.send_message(message)

        # If the drag threshold wasn't exceeded, just build a city instead.

        else:
            message = messages.CreateCity(player, end_click)
            self.gui.send_message(message)

    def fuck (self, args):
        player = self.gui.player
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        city = self.find_closest_city(position, 'all')

        # If this is one of the cities controlled by me, attempt to defend an 
        # attack.  Otherwise attempt to initiate an attack.

        if city in self.gui.player.cities:
            message = messages.DefendCity(city)
            self.gui.send_message(message)

        else:
            message = messages.AttackCity(player, city)
            self.gui.send_message(message)

    def info (self, args):
        self.gui.display_info = not self.gui.display_info
        self.gui.refresh()


    # Geometry Helpers

    def find_closest_city(self, target, city_subset='mine'):
        closest_distance = kxg.geometry.infinity
        closest_city = None

        if city_subset == 'mine':
            cities = self.gui.player.cities
        elif city_subset == 'all':
            cities = self.gui.world.yield_cities()
        else:
            message = "The second argument must be either 'mine' or 'all'."
            raise ValueError(message)

        for city in cities:
            offset = target - city.position
            distance = offset.magnitude_squared

            if distance < closest_distance:
                closest_distance = distance
                closest_city = city

        return closest_city


class Gui (kxg.Actor):

    # Settings (fold)
    background = 'white'
    text_color = 'black'
    status_font = Font('fonts/FreeSans.ttf', 14)

    city_radius = 20
    city_font = Font('fonts/FreeSans.ttf', 20)

    splash_color = 'white'
    banner_color = 'black'
    splash_font = Font('fonts/FreeSans.ttf', 54)
    banner_alpha = 0.75

    refresh_rate = 0.2
    minimum_drag_distance = 7

    def __init__(self):
        kxg.Actor.__init__(self)

        self.world = None
        self.player = None
        self.size = None
        self.hotkeys = Hotkeys(self)

        self.display_info = False
        self.splash_message = ""
        self.postgame_finished = False

    def get_name(self):
        return 'gui'

    def get_world(self):
        return self.world


    def setup(self):
        self.hotkeys.setup()

    def update(self, time):
        game_started = self.world.has_game_started()
        game_ended = self.world.has_game_ended()

        if game_started and not game_ended:
            self.draw(time)
            self.react(time)

        elif game_ended:
            self.draw(time)
            self.react_postgame(time)

        else:
            pass

    def teardown(self):
        pass


    def start_game(self):
        pygame.init()

        self.size = self.world.map.size
        self.screen = pygame.display.set_mode(self.size)

        self.timer = 0
        self.timeout = self.refresh_rate

        self.soft_refresh = True
        self.hard_refresh = True

    def game_over(self, winner):
        self.refresh()

        if self.player is winner:
            self.splash_message = "You win!"
        else:
            self.splash_message = "You lost!"

    def create_player(self, player, is_mine):
        if is_mine: self.player = player

    def create_city(self, city, is_mine):
        self.refresh()

    def create_road(self, road, is_mine):
        self.refresh()

    def attack_city(self, siege, was_me):
        self.refresh()

    def defend_city(self, siege, was_me):
        self.refresh()

    def capture_city(self, siege):
        self.refresh()

    def defeat_player(self, player):
        self.refresh()


    def reject_create_city(self, message):
        pass

    def reject_create_road(self, message):
        pass

    def reject_attack_city(self, message):
        pass

    def reject_defend_city(self, message):
        pass


    def draw(self, time):
        self.timer += time

        if self.timer < self.timeout:
            return

        self.timer = 0

        if self.hard_refresh:
            self.hard_refresh = False
            self.draw_background(self.screen)
            self.draw_roads(self.screen)
            self.draw_cities(self.screen)
            self.draw_splash(self.screen)

        self.draw_player(self.screen)

        pygame.display.flip()

    def clear(self):
        color = Color(self.background)
        self.screen.fill(color)

    def refresh(self):
        self.hard_refresh = True

    def draw_background(self, screen):
        self.clear()

        def interpolate(start, end, extent):
            return start + extent * (end - start)

        def FadedColor(source, extent):
            source_color = Color(source)

            r = interpolate(source_color.r, 255, extent)
            g = interpolate(source_color.g, 255, extent)
            b = interpolate(source_color.b, 255, extent)
            a = source_color.a

            return (r, g, b)

        # Draw the border push made by each city.
        for city in self.world.yield_cities():
            color = Color(city.player.color)
            position = city.position.pygame
            radius = city.border + 1

            pygame.draw.circle(screen, color, position, radius, 1)

        # Fill in the border with solid circles to remove internal lines.
        for city in self.world.yield_cities():
            color = Color(self.background)
            position = city.position.pygame
            radius = city.border

            pygame.draw.circle(screen, color, position, radius)

        # Draw the area in which new cities cannot be built.
        for city in self.player.cities:
            color = FadedColor(city.player.color, 0.90)
            position = city.position.pygame
            radius = city.radius

            pygame.draw.circle(screen, color, position, radius)

    def draw_player(self, screen):
        status = "Wealth: %d, %+d" % (self.player.wealth, self.player.revenue)
        color = Color(self.text_color)
        background = Color(self.background)
        text = self.status_font.render(status, True, color)

        offset = 5, 5
        rect = kxg.geometry.Rectangle.from_surface(text) + offset

        pygame.draw.rect(screen, background, rect.pygame)
        screen.blit(text, offset)

    def draw_roads (self, screen):
        for player in self.world.players:
            for road in player.roads:
                start = road.start.position.pygame
                end = road.end.position.pygame
                color = Color(player.color)

                pygame.draw.aaline(screen, color, start, end)

    def draw_cities (self, screen):
        for city in self.world.yield_cities():
            self.draw_city(screen, city)

    def draw_city(self, screen, city):
        position = city.position
        radius = self.city_radius
        city_level = "%d" % city.level
        player_color = Color(city.player.color)
        text_color = Color(self.text_color)
        fill_color = Color(self.background)
        rect_from_surface = kxg.geometry.Rectangle.from_surface

        # Draw the outline of the city itself.
        if city.is_under_siege():
            vertices = []
            iterations = 30

            for x in range(iterations):
                if x % 2:
                    magnitude = radius * random.uniform(0.4, 0.8)
                else:
                    magnitude = radius * random.uniform(0.0, 0.1)

                offset = kxg.geometry.Vector.from_degrees(x * 360 / iterations)
                vector = position + (magnitude + radius) * offset 

                vertices.append(vector.pygame)

            pygame.draw.polygon(screen, fill_color, vertices)
            pygame.draw.polygon(screen, player_color, vertices, 1)

        else:
            pygame.draw.circle(
                    screen, fill_color, position.pygame, radius)
            pygame.draw.circle(
                    screen, player_color, position.pygame, radius, 1)

        # Draw the city level.
        text_surface = self.city_font.render(
                city_level, True, text_color)
        text_rect = rect_from_surface(text_surface)
        text_position = position - text_rect.center

        screen.blit(text_surface, text_position.pygame)

        # Draw extra information regarding the price of sieging or 
        # relieving each individual city.

        if self.display_info:
            pass

    def draw_splash(self, screen):
        font = self.splash_font
        message = self.splash_message
        splash_color = Color(self.splash_color)
        banner_color = Color(self.banner_color)
        banner_alpha = int(255 * self.banner_alpha)
        rect_from_size = kxg.geometry.Rectangle.from_size
        rect_from_surface = kxg.geometry.Rectangle.from_surface
        
        if not self.splash_message:
            return

        splash_surface = font.render(message, True, splash_color)
        splash_rect = rect_from_surface(splash_surface)
        splash_rect.center = self.world.map.center

        banner_rect = rect_from_size(self.world.map.width, splash_rect.height)
        banner_rect.center = splash_rect.center
        banner_surface = pygame.Surface(banner_rect.size)
        banner_surface.fill(banner_color)
        banner_surface.set_alpha(banner_alpha)

        screen.blit(banner_surface, banner_rect.top_left.pygame)
        screen.blit(splash_surface, splash_rect.top_left.pygame)


    def react(self, time):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.postgame_finished = True
            self.hotkeys.handle(event)

    def react_postgame(self, time):
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit


