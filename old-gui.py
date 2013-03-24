from __future__ import division

import pygame
import pygame.gfxdraw

from math import *
from pygame.locals import *

import kxg
import messages
import tokens
import random

# Composite Artist?

Surface = pygame.Surface
Color = pygame.color.Color
Font = pygame.font.Font
Image = pygame.image.load

Vector = kxg.geometry.Vector
Rectangle = kxg.geometry.Rectangle

pygame.font.init()

class Gui (kxg.Actor):

    # Settings (fold)
    text_color = 'black'
    background_color = 'white'
    splash_color = 'white'
    banner_color = 'black'
    banner_alpha = 0.85

    status_font = Font('fonts/FreeSans.ttf', 14)
    city_font = Font('fonts/FreeSans.ttf', 20)
    splash_font = Font('fonts/FreeSans.ttf', 54)

    refresh_rate = 1 / 20
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

    def draw(self, time):
        self.timer += time
        if self.timer < self.timeout:
            return
        self.timer = 0

        stale_regions = []
        for artist in self.artists:
            stale_regions += artist.update(time)

        for artist in self.artists:
            for region in stale_regions:
                artist.draw(self.screen, region)

        pygame.display.update(stale_regions)
        self.hard_refresh = False

    def teardown(self):
        pass


    def start_game(self):
        pygame.init()

        self.size = self.world.map.size
        self.screen = pygame.display.set_mode(self.size)

        self.background_artist = \
                BackgroundArtist(self.world, self.player, self.size)

        self.artists = [
                self.background_artist,
                CommunityArtist(self.world),
                #RoadArtist(),
                PlayerArtist(self.player),
                #MessageArtist(),
                ]

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
        self.background_artist.redraw(city)
        self.refresh()

    def create_army(self, army, is_mine):
        self.refresh()

    def create_road(self, road, is_mine):
        self.refresh()

    def upgrade_city(self, city, is_mine):
        self.refresh()

    def upgrade_army(self, city, is_mine):
        self.refresh()

    def move_army(self, army, target, is_mine):
        pass

    def attack_city(self, siege, was_me):
        self.refresh()

    def defend_city(self, siege, was_me):
        self.refresh()

    def capture_city(self, siege):
        self.refresh()

    def defeat_player(self, player):
        self.refresh()


    def show_error(self, message):
        self.add_message(message.error)
        print message.error

    def add_message(self, string, duration=5):
        message = StatusMessage(string, duration)
        self.status_messages.append(message)


    def clear(self):
        color = Color(self.background_color)
        self.background.fill(color)

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
                color = Color(self.background_color)
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
            color = Color(self.background_color)
            position = city.position.pygame
            radius = city.buffer

            pygame.draw.circle(screen, color, position, radius)

        # Hide the regions that are within your enemy's border.
        for city in self.world.yield_cities():
            if city.player is not self.player:
                color = Color(self.background_color)
                position = city.position.pygame
                radius = city.border

                pygame.draw.circle(screen, color, position, radius)

    def draw_player(self, screen):
        color = Color(self.text_color)
        background = Color(self.background_color)

        wealth_status = "Wealth: %d, %+d" % (self.player.wealth, self.player.revenue)
        #city_status = "Build City: %d" % tokens.City.get_next_price(self.player)
        city_status = "Build City: ???"

        # The game seems to crash intermittently on the following two lines, 
        # usually with an error suggesting that either wealth_text or city_text 
        # is an empty string.  Since that doesn't make any sense, I've put this 
        # try/except block here to hopefully provide some more useful debugging 
        # information the next time the game crashes.
        
        try:
            wealth_text = self.status_font.render(wealth_status, True, color)
            city_text = self.status_font.render(city_status, True, color)
        except:
            pass

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
        background = Color(self.background_color)
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
            city.get_extension().draw(
                    screen, self.background, self.hard_refresh)

    def draw_armies (self, screen):
        for army in self.world.yield_armies():
            army.get_extension().draw(
                    screen, self.background, self.hard_refresh)

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
        banner_surface = Surface(banner_rect.size)
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


class Hotkeys (object):

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

        register_chain (['fMOUSEDOWN', left], self.fight, None)

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

        # If the drag threshold wasn't exceeded, either build or upgrade a 
        # city.  An upgrade is requested if an existing city was clicked on and 
        # a build is requested otherwise.

        else:
            city = world.find_closest_city(end_click, player, cutoff)

            if city is not None:
                message = messages.UpgradeCity(city)
                self.gui.send_message(message)

            else:
                message = messages.CreateCity(player, end_click)
                self.gui.send_message(message)

    def fight(self, args):
        world = self.gui.world
        player = self.gui.player
        cutoff = tokens.City.radius

        position = kxg.geometry.Vector.from_tuple(self.event.pos)
        army = world.find_closest_army(position, player, cutoff)

        if army is not None:
            message = messages.UpgradeArmy(army)
            self.gui.send_message(message)

        else:
            message = messages.CreateArmy(player, position)
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


class ClippingMask (object):

    def __init__(self, path):
        self.mask = pygame.image.load(path)
        self.size = self.mask.get_size()

        width, height = self.mask.get_size()
        array = pygame.PixelArray(self.mask)

        for x in range(width):
            for y in range(height):
                intensity = self.mask.unmap_rgb(array[x][y]).r
                array[x][y] = 255, 255, 255, intensity

    def apply(self, surface):
        origin = 0, 0
        blend_mode = pygame.BLEND_RGBA_MULT
        per_pixel_alpha = pygame.SRCALPHA

        assert surface.get_flags() & per_pixel_alpha
        surface.blit(self.mask, origin, special_flags=blend_mode)

        return surface

    def apply_color(self, color):
        size = self.mask.get_size()
        per_pixel_alpha = pygame.SRCALPHA

        surface = Surface(size, flags=per_pixel_alpha)
        surface.fill(color)

        return self.apply(surface)



def fade_color(source, extent=0.90):
    source_color = Color(source)

    r = interpolate_color(source_color.r, 255, extent)
    g = interpolate_color(source_color.g, 255, extent)
    b = interpolate_color(source_color.b, 255, extent)

    return (r, g, b)

def interpolate_color(start, end, extent):
    return start + extent * (end - start)


class Artist (object):

    def update(self, time):
        return []

    def draw(self, screen, region):
        pass

    def blit(self, destination, source, position, region):
        # To understand how this method works, you have to understand the 
        # precise meanings of the position and area arguments to the blit 
        # function.  The position argument is relative to the destination 
        # surface, and indicates where the blitted image will appear.  
        #
        # The area argument is relative to the source surface.  This mean that, 
        # in order to capture the entire community symbol, the area rectangle 
        # must go from (0, 0) to (80, 80).  However, the given region rectangle 
        # is relative to the screen and not the source surface.  The hideous 
        # operations shown below correct for this difference in perspective.

        region = region.move(-position[0], -position[1])
        offset = (position[0] + region.left, position[1] + region.top)
        destination.blit(source, offset, area=region)


class BackgroundArtist (Artist):

    # Settings (fold)
    background_color = 'white'

    def __init__(self, world, player, size):
        self.world = world
        self.player = player
        self.surface = pygame.Surface(size)
        self.stale_cities = []
        self.stale_everything = True

    def update(self, time):
        if not self.stale_cities and not self.stale_everything:
            return []

        background_color = Color(self.background_color)
        player_color = fade_color(self.player.color)

        surface = self.surface
        surface.fill(background_color)

        # If the player has no cities, show where the first city can be built.
        if not self.player.cities and not self.world.has_game_ended():
            surface.fill(player_color)

        # Fill in the complete extent of your territory.
        for city in self.player.cities:
            position = city.position.pygame; radius = city.border
            pygame.draw.circle(surface, player_color, position, radius)

        # Hide the regions that are too close to your other cities to build in.
        for city in self.player.cities:
            position = city.position.pygame; radius = city.buffer
            pygame.draw.circle(surface, background_color, position, radius)

        # Hide the regions that are within your enemy's border.
        for city in self.world.yield_cities():
            if city.player is not self.player:
                position = city.position.pygame; radius = city.border
                pygame.draw.circle(surface, background_color, position, radius)

        # Indicate that the entire background changed.
        if self.stale_everything:
            self.stale_everything = False
            self.stale_cities = []

            return [self.surface.get_rect()]

        # Indicate exactly which cities need to be redrawn.
        if self.stale_cities:
            stale_regions = []
            rect_from_center = kxg.geometry.Rectangle.from_center

            for city in self.stale_cities:
                position = city.position; size = 2 * city.border
                region = rect_from_center(position, size, size)
                stale_regions.append(region.pygame)

            self.stale_cities = []
            return stale_regions

    def draw(self, screen, region):
        screen.blit(self.surface, region.topleft, area=region)

    def redraw(self, city):
        self.stale_cities.append(city)
        self.stale_everything = (len(city.player.cities) == 1)


class RoadArtist (Artist):

    def draw_roads (self, screen):
        for player in self.world.players:
            for road in player.roads:
                start = road.start.position.pygame
                end = road.end.position.pygame
                color = Color(player.color)

                pygame.draw.aaline(screen, color, start, end)


class CommunityArtist (Artist):

    # Data (fold)
    white = 255, 255, 255
    transparent = 0, 0, 0, 0
    origin = 0, 0

    masks = {
            'normal shape': ClippingMask('images/normal-shape.png'),
            'battle shape': ClippingMask('images/battle-shape.png'),
            'city icon':    ClippingMask('images/city-icon.png'),
            'army icon':    ClippingMask('images/army-icon.png'),
            'full health':  ClippingMask('images/full-health.png'),
            'empty health': ClippingMask('images/empty-health.png') }

    layers = {
            'city icon':    masks['city icon'].apply_color(white),
            'army icon':    masks['army icon'].apply_color(white),
            'empty health': masks['empty health'].apply_color(white) }

    font = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 16)

    def __init__(self, world):
        self.world = world

    def update(self, time):
        stale_regions = []

        for road in self.world.yield_roads():
            extension = road.get_extension()
            stale_regions += extension.update(time)

        for city in self.world.yield_cities():
            extension = city.get_extension()
            stale_regions += extension.update(time)

        for army in self.world.yield_armies():
            extension = army.get_extension()
            stale_regions += extension.update(time)

        return stale_regions

    def draw(self, screen, region):
        for road in self.world.yield_roads():
            road.get_extension().draw(screen, region)

        for city in self.world.yield_cities():
            city.get_extension().draw(screen, region)

        for army in self.world.yield_armies():
            army.get_extension().draw(screen, region)


class PlayerArtist (Artist):

    # Settings (fold)
    text_color = 'black'
    text_font = Font('fonts/FreeSans.ttf', 14)
    background_color = 'white'

    top_left = kxg.geometry.Vector(5, 5)
    line_spacing = 5

    def __init__(self, player):
        self.player = player
        self.previous_stockpile = 0
        self.previous_city_price = 0

        self.size = 200, 2 * self.text_font.get_height() + self.line_spacing
        self.surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)

        rect_from_size = kxg.geometry.Rectangle.from_size
        self.rectangle = rect_from_size(*self.size)
        self.rectangle.top_left = self.top_left
        self.rectangle = self.rectangle.pygame


    def update(self, time):
        stockpile = int(self.player.wealth)
        #city_price = tokens.City.get_price(self.player)
        city_price = 0

        # Return immediately if nothing has changed.
        if stockpile == self.previous_stockpile:
            if city_price == self.previous_city_price:
                return []

        # Otherwise draw the updated status message.
        self.previous_stockpile = stockpile
        self.previous_city_price = city_price

        color = Color(self.text_color)
        background = Color(self.background_color)
        transparent = 0, 0, 0, 0

        surface = self.surface
        surface.fill(transparent)

        wealth_status = "Wealth: %d, %+d" % (self.player.wealth, self.player.revenue)
        #city_status = "Build City: %d" % tokens.City.get_price(self.player)
        city_status = "Build City: ???"

        wealth_text = self.text_font.render(wealth_status, True, color)
        city_text = self.text_font.render(city_status, True, color)

        wealth_rect = kxg.geometry.Rectangle.from_surface(wealth_text)
        city_rect = kxg.geometry.Rectangle.from_surface(city_text)

        wealth_offset = 0, 0
        city_offset = 0, self.line_spacing + self.text_font.get_height()
        city_rect += city_offset

        pygame.draw.rect(surface, background, wealth_rect.pygame)
        pygame.draw.rect(surface, background, city_rect.pygame)

        surface.blit(wealth_text, wealth_offset)
        surface.blit(city_text, city_offset)

        return [self.rectangle]

    def draw(self, screen, region):
        self.blit(screen, self.surface, self.top_left, region)
        #screen.blit(self.surface, self.top_left, area=region)


class MessageArtist (Artist):

    def draw_messages(self, screen):
        color = Color(self.text_color)
        background = Color(self.background_color)
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


class GameOverArtist (Artist):

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
        banner_surface = Surface(banner_rect.size)
        banner_surface.fill(banner_color)
        banner_surface.set_alpha(banner_alpha)

        screen.blit(banner_surface, banner_rect.top_left.pygame)
        screen.blit(splash_surface, splash_rect.top_left.pygame)



class CommunityExtension (Artist):

    # Data (fold)
    white = 255, 255, 255
    transparent = 0, 0, 0, 0
    origin = 0, 0

    masks = {
            'normal shape': ClippingMask('images/normal-shape.png'),
            'battle shape': ClippingMask('images/battle-shape.png'),
            'city icon':    ClippingMask('images/city-icon.png'),
            'army icon':    ClippingMask('images/army-icon.png'),
            'full health':  ClippingMask('images/full-health.png'),
            'empty health': ClippingMask('images/empty-health.png') }

    layers = {
            'city icon':    masks['city icon'].apply_color(white),
            'army icon':    masks['army icon'].apply_color(white),
            'empty health': masks['empty health'].apply_color(white) }

    font = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 16)

    def __init__(self, actor, community, type):
        rect_from_surface = kxg.geometry.Rectangle.from_surface

        self.community = community
        self.rectangle = rect_from_surface(self.masks['normal shape'].mask)
        self.rectangle.center = community.position
        self.surface = Surface(self.rectangle.size, flags=pygame.SRCALPHA)
        self.icon = self.layers['%s icon' % type]

        self.is_stale = True
        self.has_moved = False

        self.update_owner()


    def update(self, time):
        if self.has_moved:
            from_union = kxg.geometry.Rectangle.from_union
            old_rectangle = self.rectangle.copy()
            self.rectangle.center = self.community.position
            stale_rectangle = from_union(old_rectangle, self.rectangle)
            self.has_moved = False
            return [stale_rectangle.pygame]
        
        elif self.is_stale:
            self.is_stale = False
            return [self.rectangle.pygame]

        else:
            return []

    def update_level(self):
        self.redraw_surface()

    def update_health(self):
        self.redraw_surface()

    def update_owner(self):
        color = Color(self.community.player.color)
        self.normal_shape = self.masks['normal shape'].apply_color(color)
        self.battle_shape = self.masks['battle shape'].apply_color(color)
        self.redraw_surface()

    def update_position(self):
        self.has_moved = True


    def draw(self, screen, region):
        self.blit(screen, self.surface, self.rectangle.top_left, region)

    def redraw_surface(self):
        self.surface.fill(self.transparent)
        self.is_stale = True

        self.redraw_shape()
        self.redraw_icon()
        self.redraw_level()
        self.redraw_health()

    def redraw_shape(self):
        self.is_in_battle = self.community.is_in_battle()

        if self.is_in_battle:
            self.surface.blit(self.battle_shape, self.origin)
        else:
            self.surface.blit(self.normal_shape, self.origin)

    def redraw_icon(self):
        self.surface.blit(self.icon, self.origin)

    def redraw_level(self):
        self.level = self.community.get_level()
        self.level = str(self.level)

        text = self.font.render(self.level, True, self.white);
        position = ( 
                40.000 - text.get_width() / 2,
                32.015 - text.get_height() / 2 )

        self.surface.blit(text, position)

    def redraw_health(self):
        self.health = self.community.get_health()

        full_health = self.masks['full health']
        empty_health = self.layers['empty health']

        health_wedge = Surface(self.rectangle.size, flags=pygame.SRCALPHA)
        health_wedge.fill(self.transparent)

        iterations = 50
        cx, cy = health_wedge.get_size()
        cx /= 2; cy /= 2
        points = [(cx, cy)]
        health = self.community.get_health() / self.community.get_max_health()

        for i in range(iterations + 1):
            x = cx * (1 - cos(health * pi * i / iterations))
            y = cy * (1 - sin(health * pi * i / iterations))
            points.append((int(x), int(y)))

        pygame.draw.polygon(health_wedge, self.white, points)

        full_health.apply(health_wedge)

        self.surface.blit(health_wedge, self.origin)
        self.surface.blit(empty_health, self.origin)


class CityExtension (CommunityExtension):
    def __init__(self, actor, city):
        CommunityExtension.__init__(self, actor, city, 'city')

class ArmyExtension (CommunityExtension):
    def __init__(self, actor, army):
        CommunityExtension.__init__(self, actor, army, 'army')

class RoadExtension (Artist):

    def __init__(self, actor, road):
        self.actor = actor
        self.road = road
        self.surface = None
        self.area = None

    def update(self, time):
        if self.surface:
            return []

        color = Color(self.road.player.color)
        corners = self.road.start.position, self.road.end.position

        self.area = Rectangle.from_corners(*corners)
        self.area.grow(1)
        self.surface = Surface(self.area.size, flags=pygame.SRCALPHA)
        self.surface.fill((255, 255, 255, 0))

        start = self.road.start.position - self.area.top_left
        end = self.road.end.position - self.area.top_left
        pygame.draw.aaline(self.surface, color, start.pygame, end.pygame)

        return [self.area.pygame]

    def draw(self, screen, region):
        self.blit(screen, self.surface, self.area.top_left, region)

