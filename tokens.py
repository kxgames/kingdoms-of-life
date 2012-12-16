from __future__ import division

import kxg
import messages
import random

class World (kxg.World):

    def __init__ (self):
        kxg.World.__init__(self)

        self.players = []
        self.map = kxg.geometry.Rectangle.from_size(500, 500)
        self.winner = None

        self.game_started = False
        self.game_ended = False


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        for player in self.players:
            player.update(time)

    @kxg.check_for_safety
    def teardown(self):
        pass


    @kxg.check_for_safety
    def start_game(self):
        self.game_started = True

    @kxg.check_for_safety
    def game_over(self, winner):
        self.game_ended = True
        self.winner = winner

    def has_game_started (self):
        return self.game_started

    def has_game_ended (self):
        return self.game_ended


    @kxg.check_for_safety
    def create_player(self, player):
        self.players.append(player)
        self.add_token(player)
        player.setup(self)

    @kxg.check_for_safety
    def create_city(self, player, city, price):
        player.cities.append(city)
        player.spend_wealth(price)
        self.add_token(city)
        city.setup()

    @kxg.check_for_safety
    def create_road(self, player, road, price):
        player.roads.append(road)
        player.spend_wealth(price)
        self.add_token(road)
        road.setup()

    @kxg.check_for_safety
    def attack_city(self, attacker, siege, price):
        attacker.sieges.append(siege)
        attacker.spend_wealth(price)
        self.add_token(siege)
        siege.setup()

    @kxg.check_for_safety
    def defend_city(self, defender, siege, price):
        self.remove_token(siege)
        defender.spend_resource(price)
        siege.attacker.sieges.remove(siege)
        siege.teardown()

    @kxg.check_for_safety
    def capture_city(self, defender, siege):
        city.player = siege.attacker
        siege.defender.cities.remove(city)
        siege.attacker.cities.append(city)

        self.remove_token(siege)
        siege.attacker.sieges.remove(siege)
        siege.teardown()

    @kxg.check_for_safety
    def defeat_player(self, player):
        self.remove_token(player)
        self.players.remove(player)
        player.teardown()
    

class Referee (kxg.Referee):

    def __init__(self):
        kxg.Referee.__init__(self)
        self.world = None

    def get_name(self):
        return 'referee'

    def is_finished(self):
        return self.world.has_game_ended()


    def setup(self, world):
        self.world = world
        self.send_message(messages.StartGame())

    def update(self, time):
        # Check to see if any players have successfully captured a city.
        for player in self.world.players:
            for siege in player.sieges:
                if siege.was_successful():
                    message = messages.CaptureCity(siege)
                    self.send_message(message)

    def teardown(self):
        pass


    def start_game(self):
        pass

    def create_player(self, player, is_mine):
        assert not is_mine

    def create_city(self, city, is_mine):
        assert not is_mine

    def create_road(self, road, is_mine):
        assert not is_mine

    def attack_city(self, siege, is_mine):
        assert not is_mine

    def defend_city(self, siege, is_mine):
        assert not is_mine

    def capture_city(self, siege):
        # Check to see if the defender has lost.
        if siege.defender.was_defeated():
            message = DefeatPlayer(player)
            self.send_message(message)

    def defeat_player(self, player):
        if len(world.players) == 1:
            winner = self.world.players[0]
            message = GameOver(winner)
            self.send_message(message)



class Player (kxg.Token):

    # Settings (fold)
    starting_wealth = 100
    starting_revenue = 25
    
    def __init__(self, name, color):
        kxg.Token.__init__(self)

        self.name = name
        self.color = color
        self.world = None
        self.cities = []
        self.roads = []
        self.sieges = []

        self.wealth = self.starting_wealth
        self.revenue = self.starting_revenue


    @kxg.check_for_safety
    def setup(self, world):
        self.world = world

    @kxg.check_for_safety
    def update(self, time):
        for city in self.cities: city.update(time)
        for road in self.roads: road.update(time)
        for siege in self.sieges: siege.update(time)

        self.revenue = self.starting_revenue

        for road in self.roads:
            self.revenue += road.get_revenue()

        self.wealth += time * self.revenue / 30

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    def spend_wealth(self, price):
        self.wealth -= price

    def can_afford_price(self, price):
        return price <= self.wealth

    def can_place_city(self, city):
        return True

    def can_place_road(self, road):
        return True


class City (kxg.Token):

    # Settings (fold)
    radius = 25
    border = 50

    @staticmethod
    def get_next_price(player):
        return 20 + 10 * len(player.cities)

    @staticmethod 
    def get_next_level():
        level = random.paretovariate(1)
        return min(20, int(level))


    def __init__(self, player, position):
        kxg.Token.__init__(self)

        self.player = player
        self.position = position

        self.level = 0; self.roads = 0
        self.under_seige = False


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


class Road (kxg.Token):

    # Settings (fold)
    tax_rate = 1.00

    def __init__(self, player, start, end):
        kxg.Token.__init__(self)

        self.player = player
        self.start = start
        self.end = end

    def get_revenue(self):
        """ Return the revenue generated by this road in 30 seconds. """
        return self.tax_rate * (self.start.level + self.end.level)

    def get_price(self):
        displacement = self.start.position - self.end.position
        distance = displacement.magnitude
        return 30 + distance / 10


    @kxg.check_for_safety
    def setup(self):
        self.start.roads += 1
        self.end.roads += 1

    @kxg.check_for_safety
    def update(self, time):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


class Siege (kxg.Token):

    # Settings (fold)
    time_until_capture = 25

    def __init__(self, attacker, city):
        kxg.Token.__init__()
        self.city = city
        self.attacker = attacker
        self.defender = city.player
        self.elapsed_time = 0

    def get_attack_price(self):
        return 50 * self.city.level

    def get_defense_price(self):
        return 50 * self.city.roads + 50

    def was_successful(self):
        return self.elapsed_time >= self.time_until_capture


    @kxg.check_for_safety
    def setup(self):
        for city in self.defender.cities:
            city.under_siege = True

    @kxg.check_for_safety
    def update(self, time):
        self.elapsed_time += time

    @kxg.check_for_safety
    def teardown(self):
        for city in self.defender.cities:
            city.under_siege = True

