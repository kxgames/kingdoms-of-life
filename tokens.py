from __future__ import division

import kxg
import messages
import gui
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
    def create_army(self, army, price):
        self.add_token(army)
        army.player.armies.append(army)
        army.player.spend_wealth(price)
        army.setup()

    @kxg.check_for_safety
    def create_road(self, road, price):
        self.add_token(road)
        road.player.roads.append(road)
        road.player.spend_wealth(price)
        road.setup()

    @kxg.check_for_safety
    def upgrade_city(self, city, price):
        city.upgrade()
        city.player.spend_wealth(price)

    @kxg.check_for_safety
    def upgrade_army(self, army, price):
        army.upgrade()
        army.player.spend_wealth(price)

    @kxg.check_for_safety
    def attack_city(self, battle, price):
        self.add_token(battle)
        battle.attacker.battles.append(battle)
        battle.attacker.spend_wealth(price)
        battle.setup()

    @kxg.check_for_safety
    def defend_city(self, battle, price):
        battle.defender.spend_wealth(price)
        battle.attacker.battles.remove(battle)
        battle.teardown()
        self.remove_token(battle)

    @kxg.check_for_safety
    def capture_city(self, battle):
        city = battle.city
        attacker = battle.attacker
        defender = battle.defender

        # Give control of the city to the attacker.
        city.player = attacker
        defender.cities.remove(city)
        attacker.cities.append(city)

        # Remove the battle object.
        attacker.battles.remove(battle)
        battle.teardown()
        self.remove_token(battle)

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

    def find_closest_army(self, target, player=None, cutoff=None):
        closest_distance = kxg.geometry.infinity
        closest_army = None

        if player is None:
            armies = self.yield_armies()
        else:
            armies = player.armies

        for army in armies:
            offset = target - army.position
            distance = offset.magnitude

            if distance < closest_distance:
                closest_distance = distance
                closest_army = army

        if (cutoff is not None) and (closest_distance > cutoff):
            return None

        return closest_army


    def yield_cities(self):
        for player in self.players:
            for city in player.cities:
                yield city

    def yield_armies(self):
        for player in self.players:
            for army in player.armies:
                yield army

    def yield_roads(self):
        for player in self.players:
            for road in player.roads:
                yield road

    def yield_battles(self):
        for player in self.players:
            for battle in player.battle:
                yield battle


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
            for battle in player.battles:
                if battle.was_successful():
                    message = messages.CaptureCity(battle)
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

    def create_army(self, army, is_mine):
        assert not is_mine

    def create_road(self, road, is_mine):
        assert not is_mine

    def upgrade_city(self, city, is_mine):
        assert not is_mine

    def upgrade_army(self, army, is_mine):
        assert not is_mine

    def attack_city(self, battle, is_mine):
        assert not is_mine

    def defend_city(self, battle, is_mine):
        assert not is_mine

    def capture_city(self, battle):
        # Check to see if the defender has lost.
        if battle.defender.was_defeated():
            message = messages.DefeatPlayer(battle.defender)
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
        self.armies = []
        self.roads = []
        self.battles = []

        self.wealth = self.starting_wealth
        self.revenue = self.starting_revenue


    @kxg.check_for_safety
    def setup(self, world):
        self.world = world

    @kxg.check_for_safety
    def update(self, time):
        for city in self.cities: city.update(time)
        for road in self.roads: road.update(time)
        for battle in self.battles: battle.update(time)

        self.revenue = self.starting_revenue

        for road in self.roads:
            self.revenue += road.get_revenue()

        self.wealth += time * self.revenue / 30

    def signal(self, referee):
        pass

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

    def can_place_army(self, city):
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

    def find_closest_army(self, target, cutoff=None):
        return self.world.find_closest_army(target, self, cutoff)

    def was_defeated(self):
        return not self.cities


class Community (kxg.Token):

    def __init__(self):
        self.level = 1
        self.health = self.get_max_health()
        self.battle = None

        kxg.Token.__init__(self)


    def upgrade(self):
        health_percent = self.health / self.get_max_health()
        self.level += 1
        self.health = health_percent * self.get_max_health()


    def get_level(self):
        return self.level

    def get_health(self):
        return self.health

    def get_max_health(self):
        raise NotImplementedError

    def get_attack(self):
        raise NotImplementedError

    def get_supply(self):
        raise NotImplementedError

    def get_distance_to(self, other):
        return self.position.get_distance(other.position)

    def is_in_battle(self):
        return self.battle is not None


class City (Community):

    # Settings (fold)
    radius = 27
    buffer = 90
    border = 130

    def __init__(self, player, position):
        self.player = player
        self.position = position
        self.roads = []

        Community.__init__(self)

    def __extend__(self):
        return {'gui': gui.CityExtension}


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        pass

    def signal(self, referee):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    def get_price(self):
        return 20 + 10 * len(self.player.cities)

    def get_upgrade_price(self):
        return 10 * self.level

    def get_max_health(self):
        return 20 + 5 * self.level

    def get_attack(self, time):
        return 2 + self.level // 2

    def get_supply(self):
        return sum([road.get_supply_to(self) for road in self.roads], 1)
    

class Army (Community):

    def __init__(self, player, position):
        self.player = player
        self.position = position

        Community.__init__(self)

    def __extend__(self):
        return {'gui': gui.ArmyExtension}


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        pass

    def signal(self, referee):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    def get_price(self):
        return 30 + 10 * len(self.player.cities)

    def get_upgrade_price(self):
        return 10 * self.level

    def get_max_health(self):
        return 15 * 4 * self.level

    def get_attack(self):
        return 10 + 2 * self.level

    def get_supply(self):
        city_supplies = []

        for city in self.player.cities:
            city_supply = city.get_supply()
            city_supplies.append(city_supply)

        return max(city_supplies)


class Road (kxg.Token):

    def __init__(self, player, start, end):
        kxg.Token.__init__(self)
        self.player = player
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.start
        yield self.end


    @kxg.check_for_safety
    def setup(self):
        self.start.roads.append(self)
        self.end.roads.append(self)

    @kxg.check_for_safety
    def update(self, time):
        pass

    def signal(self, referee):
        pass

    @kxg.check_for_safety
    def teardown(self):
        self.start.roads.remove(self)
        self.end.roads.remove(self)


    def get_price(self):
        return 20 + 10 * len(self.player.roads)

    def get_revenue(self):
        """ Return the revenue generated by this road in 30 seconds. """
        if self.start.is_in_battle() or self.end.is_in_battle():
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


class Battle (kxg.Token):

    # Settings (fold)
    time_until_capture = 25

    def __init__(self, attacker, city):
        kxg.Token.__init__(self)
        self.city = city
        self.attacker = attacker
        self.defender = city.player
        self.elapsed_time = 0


    @kxg.check_for_safety
    def setup(self):
        self.city.battle = self

    @kxg.check_for_safety
    def update(self, time):
        self.elapsed_time += time

    def signal(self, referee):
        pass

    @kxg.check_for_safety
    def teardown(self):
        self.city.battle = None


    def get_initiation_price(self):
        pass

    def get_retreat_cost(self):
        pass

    def was_successful(self):
        return self.elapsed_time >= self.time_until_capture



