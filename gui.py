from __future__ import division

import pygame
from pygame.locals import *

import kxg
import messages
import tokens
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
        
        self.start_click = None

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

        d_lens = {
                e2s[MOUSEBUTTONUP]    : 'dMOUSEBUTTONUP',
                e2s[MOUSEBUTTONDOWN ] : 'dMOUSEBUTTONDOWN' }

        f_lens = {
                e2s[MOUSEBUTTONUP]    : 'fMOUSEUP',
                e2s[MOUSEBUTTONDOWN]  : 'fMOUSEDOWN' }

        space_lens = {
                e2s[MOUSEBUTTONUP]    : 'iMOUSEUP',
                e2s[MOUSEBUTTONDOWN]  : 'iMOUSEDOWN' }

        self.keychain.register_lens (k2s[ K_d ], d_lens)
        self.keychain.register_lens (k2s[ K_f ], f_lens)
        self.keychain.register_lens (k2s[ K_SPACE ], space_lens)

    def setup_hotkeys (self):

        ## Register keyboard hotkeys
        register_keys = self.keychain.register_chain_key
        register_chain = self.keychain.register_chain
        register_mouse = self.keychain.register_chain_mouse

        left = kxg.gui.mouse_to_string[1]

        develop_init = ['dMOUSEBUTTONDOWN', left]
        register_chain (develop_init, self.develop_init, None)

        develop = ['dMOUSEBUTTONDOWN', left, 'dMOUSEBUTTONUP', left]
        register_chain (develop, self.develop, None)

        register_chain (['fMOUSEDOWN', left], self.fuck, None)

        #info_init = ['iMOUSEDOWN', left]
        #register_chain (info_init, self.info_init, None)

        #info = ['iMOUSEDOWN', left, 'iMOUSEUP', left]
        #register_chain (info, self.info, None)

        register_mouse([MOUSEBUTTONDOWN, 1], self.info_init)
        register_mouse([MOUSEBUTTONUP, 1], self.info)

    def handle (self, event):
        self.event = event

        if event.type == KEYDOWN:
            self.keychain.handle_key (event.key)

        elif event.type == KEYUP:
            self.keychain.handle_key (event.key, True)

        elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            self.keychain.handle_event(event.type)
            self.keychain.handle_mouse(event.button)

        else:
            pass


    # Callbacks

    def develop_init(self, args):
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.start_click = position

    def develop(self, args):
        world = self.gui.world
        player = self.gui.player
        cutoff = tokens.City.radius

        start_click = self.start_click
        end_click = kxg.geometry.Vector.from_tuple(self.event.pos)

        drag_vector = end_click - self.start_click
        drag_distance = drag_vector.magnitude

        # If the actual drag distance exceeds the minimum drag threshold, then 
        # build a road.  This requires finding the two cities nearest the 
        # end-points of the drag event.

        if drag_distance >= self.gui.minimum_drag_distance:
            start_city = world.find_closest_city(start_click, player, cutoff)
            end_city = world.find_closest_city(end_click, player, cutoff)

            if start_city is not None and end_city is not None:
                message = messages.CreateRoad(player, start_city, end_city)
                self.gui.send_message(message)

        # If the drag threshold wasn't exceeded, just build a city instead.

        else:
            message = messages.CreateCity(player, end_click)
            self.gui.send_message(message)

    def fuck(self, args):
        world = self.gui.world
        player = self.gui.player
        cutoff = tokens.City.radius

        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        city = world.find_closest_city(position, cutoff=cutoff)

        if city is None:
            return

        # If this is one of the cities controlled by me, attempt to defend an 
        # attack.  Otherwise attempt to initiate an attack.

        if city in self.gui.player.cities:
            message = messages.DefendCity(city)
            self.gui.send_message(message)

        else:
            message = messages.AttackCity(player, city)
            self.gui.send_message(message)

    def info_init(self):
        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        self.start_click = position

    def info(self):
        world = self.gui.world
        player = self.gui.player
        cutoff = tokens.City.radius
        show = self.gui.add_message

        start_click = self.start_click
        end_click = kxg.geometry.Vector.from_tuple(self.event.pos)

        drag_vector = end_click - start_click
        drag_distance = drag_vector.magnitude

        self.gui.refresh()

        # If the actual drag distance exceeds the minimum drag threshold, then 
        # show the price of a road between those two cities.

        if drag_distance >= self.gui.minimum_drag_distance:
            start_city = world.find_closest_city(start_click, player, cutoff)
            end_city = world.find_closest_city(end_click, player, cutoff)

            if start_city is not None and end_city is not None:
                message = messages.CreateRoad(player, start_city, end_city)
                show("Build road: %d" % message.price)

        # If the drag threshold wasn't exceeded, show how much it would cost to 
        # attack or defend the selected city.

        else:
            city = world.find_closest_city(end_click, cutoff=cutoff)

            if city is None:
                return

            if city in player.cities:
                defense_price = city.get_defense_price()
                show("Defend city: %d" % defense_price)
            else:
                attack_price = city.get_attack_price(player)
                show("Attack city: %d" % attack_price)


class StatusMessage (object):

    def __init__(self, message, duration):
        self.message = message
        self.timer = kxg.tools.Timer(duration)

    def __str__(self):
        return self.message

    def update(self, time):
        self.timer.update(time)

    def has_expired(self):
        return self.timer.has_expired()


class Gui (kxg.Actor):

    # Settings (fold)
    background = 'white'
    text_color = 'black'
    splash_color = 'white'
    banner_color = 'black'
    banner_alpha = 0.85

    status_font = Font('fonts/FreeSans.ttf', 14)
    city_font = Font('fonts/FreeSans.ttf', 20)
    splash_font = Font('fonts/FreeSans.ttf', 54)

    refresh_rate = 0.2
    minimum_drag_distance = 7

    def __init__(self):
        kxg.Actor.__init__(self)

        self.world = None
        self.player = None
        self.size = None
        self.hotkeys = Hotkeys(self)

        self.splash_message = ""
        self.status_messages = []
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

        for message in self.status_messages[:]:
            message.update(time)
            if message.has_expired():
                self.status_messages.remove(message)
                self.refresh()

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
            self.splash_message = "You won!"
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

    def add_message(self, string, duration=5):
        message = StatusMessage(string, duration)
        self.status_messages.append(message)


    def reject_create_city(self, message):
        self.add_message(message.error)

    def reject_create_road(self, message):
        self.add_message(message.error)

    def reject_attack_city(self, message):
        self.add_message(message.error)

    def reject_defend_city(self, message):
        self.add_message(message.error)


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
        self.draw_messages(self.screen)

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

        # If the player has no cities, show where the first city can be built.
        if not self.player.cities and not self.world.has_game_ended():
            color = FadedColor(self.player.color, 0.90)
            self.screen.fill(color)

            for city in self.world.yield_cities():
                color = Color(self.background)
                position = city.position.pygame
                radius = city.border

                pygame.draw.circle(screen, color, position, radius)

            return

        # Fill in the complete extent of your territory.
        for city in self.player.cities:
            color = FadedColor(city.player.color, 0.90)
            position = city.position.pygame
            radius = city.border

            pygame.draw.circle(screen, color, position, radius)

        # Hide the regions that are too close to your other cities to build in.
        for city in self.player.cities:
            color = Color(self.background)
            position = city.position.pygame
            radius = city.buffer

            pygame.draw.circle(screen, color, position, radius)

        # Hide the regions that are within your enemy's border.
        for city in self.world.yield_cities():
            if city.player is not self.player:
                color = Color(self.background)
                position = city.position.pygame
                radius = city.border

                pygame.draw.circle(screen, color, position, radius)

    def draw_player(self, screen):
        color = Color(self.text_color)
        background = Color(self.background)

        wealth_status = "Wealth: %d, %+d" % (self.player.wealth, self.player.revenue)
        city_status = "Build City: %d" % tokens.City.get_next_price(self.player)

        # The game seems to crash intermittently on the following two lines, 
        # usually with an error suggesting that either wealth_text or city_text 
        # is an empty string.  Since that doesn't make any sense, I've put this 
        # try/except block here to hopefully provide some more useful debugging 
        # information the next time the game crashes.
        
        try:
            wealth_text = self.status_font.render(wealth_status, True, color)
            city_text = self.status_font.render(city_status, True, color)
        except:
            print 'self.status_font =', self.status_font
            print 'wealth_status = "%s"' % wealth_status
            print 'city_status = "%s"' % city_status
            print 'color =', color

        wealth_offset = 5, 5
        city_offset = 5, 5 + wealth_text.get_height()

        wealth_rect = kxg.geometry.Rectangle.from_surface(wealth_text) + wealth_offset
        city_rect = kxg.geometry.Rectangle.from_surface(city_text) + city_offset

        pygame.draw.rect(screen, background, wealth_rect.pygame)
        pygame.draw.rect(screen, background, city_rect.pygame)

        screen.blit(wealth_text, wealth_offset)
        screen.blit(city_text, city_offset)

    def draw_messages(self, screen):
        color = Color(self.text_color)
        background = Color(self.background)
        last_offset = self.world.map.bottom - 5

        for message in self.status_messages:
            status = str(message)
            text = self.status_font.render(status, True, color)

            rectangle = kxg.geometry.Rectangle.from_surface(text)
            rectangle.center_x = self.world.map.center_x
            rectangle.bottom = last_offset

            last_offset = rectangle.top

            pygame.draw.rect(screen, background, rectangle.pygame)
            screen.blit(text, rectangle.top_left.pygame)

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
        radius = city.radius
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
                raise SystemExit
            else:
                self.hotkeys.handle(event)

    def react_postgame(self, time):
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit


