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
    def create_city(self, city, price):
        self.add_token(city)
        city.player.cities.append(city)
        city.player.spend_wealth(price)
        city.setup()

    @kxg.check_for_safety
    def create_road(self, road, price):
        self.add_token(road)
        road.player.roads.append(road)
        road.player.spend_wealth(price)
        road.setup()

    @kxg.check_for_safety
    def attack_city(self, siege, price):
        self.add_token(siege)
        siege.attacker.sieges.append(siege)
        siege.attacker.spend_wealth(price)
        siege.setup()

    @kxg.check_for_safety
    def defend_city(self, siege, price):
        siege.defender.spend_wealth(price)
        siege.attacker.sieges.remove(siege)
        siege.teardown()
        self.remove_token(siege)

    @kxg.check_for_safety
    def capture_city(self, siege):
        city = siege.city
        attacker = siege.attacker
        defender = siege.defender

        # Give control of the city to the attacker.
        city.player = attacker
        defender.cities.remove(city)
        attacker.cities.append(city)

        # Remove the siege object.
        attacker.sieges.remove(siege)
        siege.teardown()
        self.remove_token(siege)

        # Remove all the existing roads into this city.
        for road in defender.roads[:]:
            if road.has_terminus(city):
                defender.roads.remove(road)
                road.teardown()
                self.remove_token(road)

    @kxg.check_for_safety
    def defeat_player(self, player):
        self.players.remove(player)
        player.teardown()
        self.remove_token(player)
    

    def find_closest_city(self, target, player=None, cutoff=None):
        closest_distance = kxg.geometry.infinity
        closest_city = None

        if player is None:
            cities = self.yield_cities()
        else:
            cities = player.cities

        for city in cities:
            offset = target - city.position
            distance = offset.magnitude

            if distance < closest_distance:
                closest_distance = distance
                closest_city = city

        if (cutoff is not None) and (closest_distance > cutoff):
            return None

        return closest_city


    def yield_cities(self):
        for player in self.players:
            for city in player.cities:
                yield city

    def yield_roads(self):
        for player in self.players:
            for road in player.roads:
                yield road

    def yield_sieges(self):
        for player in self.players:
            for siege in player.siege:
                yield siege


class Referee (kxg.Referee):

    def __init__(self):
        kxg.Referee.__init__(self)
        self.world = None

    def get_name(self):
        return 'referee'


    def setup(self):
        message = messages.StartGame()
        self.send_message(message)

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

    def game_over(self, winner):
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
            message = messages.DefeatPlayer(siege.defender)
            self.send_message(message)

    def defeat_player(self, player):
        if len(self.world.players) == 1:
            winner = self.world.players[0]
            message = messages.GameOver(winner)
            self.send_message(message)



class Player (kxg.Token):

    # Settings (fold)
    starting_wealth = 500
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
        pass


    def spend_wealth(self, price):
        self.wealth -= price

    def can_afford_price(self, price):
        return price <= self.wealth

    def can_place_city(self, city):
        inside_buffer = False
        inside_border = False
        inside_opponent = False

        for other in self.world.yield_cities():
            offset = city.position - other.position
            distance = offset.magnitude

            inside_buffer = (distance <= other.buffer) or inside_buffer

            if other.player is self:
                inside_border = (distance <= other.border) or inside_border
            else:
                inside_opponent = (distance <= other.border) or inside_opponent 

        if inside_opponent:
            return False

        if not self.cities:
            return True

        if inside_buffer:
            return False

        if not inside_border:
            return False

        return True

    def can_place_road(self, road):

        def road_inside_city(road, city, padding):
            return kxg.geometry.circle_touching_line(
                    city.position, city.radius + padding,
                    road.start.position, road.end.position)

        for city in self.world.yield_cities():
            if city in road:
                continue

            if road_inside_city(road, city, padding=2):
                return False

        return True

    def find_closest_city(self, target, cutoff=None):
        return self.world.find_closest_city(target, self, cutoff)

    def was_defeated(self):
        return not self.cities


class City (kxg.Token):

    # Settings (fold)
    radius = 20
    buffer = 50
    border = 80

    @staticmethod
    def get_next_price(player):
        return 20 + 10 * len(player.cities)

    @staticmethod 
    def get_next_level():
        return int(random.triangular(10)) + 1


    def __init__(self, player, position):
        kxg.Token.__init__(self)

        self.player = player
        self.position = position

        self.level = 0
        self.roads = []
        self.siege = None

    def get_attack_price(self, attacker):
        prices = [kxg.geometry.infinity]
        clamp = kxg.geometry.clamp
        fixed_price = 50

        for city in attacker.cities:
            supply_level = city.get_supply_level()
            supply_price = clamp(10 * (30 - supply_level), 0, 300)

            distance = city.get_distance_to(self)
            distance_price = clamp(2 * (distance - self.border), 0, 300)

            price = fixed_price + supply_price + distance_price
            prices.append(price)

        return min(prices)

    def get_defense_price(self):
        fixed_price = 50
        clamp = kxg.geometry.clamp

        supply_level = self.get_supply_level()
        supply_price = clamp(10 * (30 - supply_level), 0, 300)

        return fixed_price + supply_price

    def get_distance_to(self, other):
        return self.position.get_distance(other.position)

    def get_supply_level(self):
        return sum([road.get_supply_to(self) for road in self.roads], 1)

    def is_under_siege(self):
        return self.siege is not None


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

    def __init__(self, player, start, end):
        kxg.Token.__init__(self)
        self.player = player
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.start
        yield self.end

    def get_price(self):
        displacement = self.start.position - self.end.position
        distance = displacement.magnitude
        return 30 + distance / 10

    def get_revenue(self):
        """ Return the revenue generated by this road in 30 seconds. """
        if self.start.is_under_siege() or self.end.is_under_siege():
            return 0
        else:
            return self.start.level + self.end.level

    def get_supply_to(self, city):
        assert self.has_terminus(city)

        if city is self.start:
            return self.end.level

        if city is self.end:
            return self.start.level

    def has_same_route(self, other):
        forwards =  (other.start is self.start and other.end is self.end)
        backwards = (other.start is self.end   and other.end is self.start)
        return forwards or backwards

    def has_terminus(self, city):
        return (self.start is city) or (self.end is city)


    @kxg.check_for_safety
    def setup(self):
        self.start.roads.append(self)
        self.end.roads.append(self)

    @kxg.check_for_safety
    def update(self, time):
        pass

    @kxg.check_for_safety
    def teardown(self):
        self.start.roads.remove(self)
        self.end.roads.remove(self)


class Siege (kxg.Token):

    # Settings (fold)
    time_until_capture = 25

    def __init__(self, attacker, city):
        kxg.Token.__init__(self)
        self.city = city
        self.attacker = attacker
        self.defender = city.player
        self.elapsed_time = 0

    def was_successful(self):
        return self.elapsed_time >= self.time_until_capture


    @kxg.check_for_safety
    def setup(self):
        self.city.siege = self

    @kxg.check_for_safety
    def update(self, time):
        self.elapsed_time += time

    @kxg.check_for_safety
    def teardown(self):
        self.city.siege = None

