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

    @kxg.check_for_safety
    def create_player (self, player)
        self.players.append(player)
        self.add_token(player)

    def has_game_started (self):
        return self.game_started


class Player (kxg.Token):

    def __init__ (self, id):
        kxg.Token.__init__(self, id)

        self.name = ""
        self.color = ""
        self.money = 0
        self.cities = []
        self.roads = []

    def setup (self, name, color):
        self.name = name
        self.color = color

    def build_city (self, position):
        ##self.cities.append( City(position))

    def build_road (self, start_city, end_city):
        ##self.append( Road (start_city, end_city))

class  City (kxg.Token):

    def __init__ (self, id, position):
        kxg.Token.__init__ (self, id)
