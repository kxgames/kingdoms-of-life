from __future__ import division

import kxg
import messages

class World (kxg.World):

    def __init__ (self):
        kxg.World.__init__(self)

        self.players = []
        self.game_started = False
        self.game_ended = False

    @kxg.check_for_safety
    def start_game(self, settings):

        # Because the nations are created by greeting messages, they are
        # created before the settings are sent out.  For convenience, their
        # setup methods are not called until the settings have been received.

        self.settings = settings
        self.game_started = True

        for nation in self.nations:
            nation.setup(self)

    def has_game_started (self):
        return self.game_started

    @kxg.check_for_safety
    def create_player(self, player)
        self.players.append(player)
        self.add_token(player)

    @kxg.check_for_safety
    def create_city(self, player, city):
        player.cities.append(city)
        self.add_token(city)

    @kxg.check_for_safety
    def create_road(self, player, road):
        player.roads.append(road)
        self.add_token(road)


class Player (kxg.Token):

    def __init__(self, name, color):
        kxg.Token.__init__(self, id)

        self.name = name
        self.color = color
        self.money = 0
        self.cities = []
        self.roads = []
        self.sieges = []

    def can_build_city(self, city):
        return True

    def can_place_city(self, city):
        return True

    def can_build_road(self, road):
        return True

    def can_place_road(self, road):
        return True


class City (kxg.Token):

    price = lambda cities: 100 + 50 * cities
    next_level = lambda: min(20, int(random.paretovariate(1)))
    radius = 25
    border = 50

    def __init__(self, player, position):
        kxg.Token.__init__(self)
        self.position = position

        self.level = 0
        self.under_seige = False


class Road (kxg.Token):

    price = lambda distance: 100 + 2 * distance

    def __init__(self, start, end):
        kxg.Token.__init__(self)
        self.start = start
        self.end = end


class Siege (kxg.Tokens):

    time_until_capture = 25

    def __init__(self, city):
        kxg.Token.__init__()
        self.city = city
        self.elapsed_time = 0

