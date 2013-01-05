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
    def request_battle(self, campaign):
        self.add_token(campaign)
        campaign.setup()
        campaign.army.chase(campaign)

    @kxg.check_for_safety
    def start_battle(self, campaign, battle):

        if isinstance(campaign.community, Army):
            cancelled_campaign = campaign.community.my_campaign
            if cancelled_campaign:
                cancelled_campaign.teardown()
                self.remove_token(cancelled_campaign)

        self.add_token(battle)
        battle.setup()

        campaign.teardown()
        self.remove_token(campaign)

    @kxg.check_for_safety
    def join_battle(self, campaign, battle):
        battle.add_community(campaign.army)

        campaign.teardown()
        self.remove_token(campaign)

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
        kxg.Referee.update(self, time)

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

    def request_battle(self, campaign, is_mine):
        assert not is_mine

    def start_battle(self, battle):
        pass

    def join_battle(self, battle):
        pass

    def move_army(self, army, target, is_mine):
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
        self.revenue = self.starting_revenue

        for road in self.roads:
            self.revenue += road.get_revenue()

        self.wealth += time * self.revenue / 30

    def report(self, messenger):
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

    # Settings (fold)
    radius = 27
    engagement_range = 3

    def __init__(self, player, position):
        kxg.Token.__init__(self)

        self.player = player
        self.position = position

        self.level = 1
        self.health = self.get_max_health()
        self.battle = None
        self.campaigns = []


    def upgrade(self):
        health_percent = self.health / self.get_max_health()
        self.level += 1
        self.health = health_percent * self.get_max_health()

        for extension in self.get_extensions():
            extension.update_level()

    def damage(self, delta):
        self.health -= delta

        for extension in self.get_extensions():
            extension.update_health()

    def add_campaign(self, campaign):
        self.campaigns.append(campaign)

    def forget_campaign(self, campaign):
        raise NotImplementedError

    def engage_battle(self, battle):
        raise NotImplementedError


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

    def get_battle_price(self):
        raise NotImplementedError

    def check_battle_proximity(self, battle):
        communities = battle.communities
        for player in battle.communities.keys():
            if self.player is not player:
                for community in communities[player]:
                    if self.check_engagement_proximity(community):
                        return True
        return False

    def check_engagement_proximity(self, community):
        radius = self.radius + community.radius + self.engagement_range
        distance = community.position - self.position
        
        return radius >= distance.magnitude

    def is_in_battle(self):
        return self.battle is not None


class City (Community):

    # Settings (fold)
    buffer = 90
    border = 130

    def __init__(self, player, position):
        Community.__init__(self, player, position)

        self.roads = []

    def __extend__(self):
        return {'gui': gui.CityExtension}


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        pass

    def report(self, messenger):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    def forget_campaign(self, campaign):
        try:
            self.campaigns.remove(campaign)
        except ValueError:
            pass

    def engage_battle(self, battle):
        self.battle = battle


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
    
    def get_battle_price(self):
        return 100


class Army (Community):

    # Settings (fold)
    speed = 25

    def __init__(self, player, position):
        Community.__init__(self, player, position)

        self.my_campaign = None
        self.target = None

    def __extend__(self):
        return {'gui': gui.ArmyExtension}


    @kxg.check_for_safety
    def setup(self):
        pass

    @kxg.check_for_safety
    def update(self, time):
        if self.my_campaign:
            target_community = self.my_campaign.community
            start = self.position
            end = target_community.position
            radius = self.radius + target_community.radius
            
            # Do pathfinding stuff

            direction = end - start
            path = direction * (1 - radius / direction.magnitude)

            self.target = start + path

        if self.target:
            heading = self.target - self.position
            if heading.magnitude < 1:
                self.target = None
            else:
                self.position += heading.get_scaled(self.speed * time)

    def report(self, messenger):
        pass

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    def chase (self, campaign):
        self.my_campaign = campaign

    def can_request_battle(self, community):
        return True


    def forget_campaign(self, campaign):
        if campaign:
            try:
                self.campaigns.remove(campaign)
            except ValueError:
                pass

            if self.my_campaign is campaign:
                self.my_campaign = None
                self.target = None
        
    def engage_battle(self, battle):
        self.battle = battle
        self.target = None
        self.forget_campaign(self.my_campaign)

    def move_to(self, target):
        self.target = target


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

    def get_battle_price(self):
        return 0

    def can_move_to(self, position):
        return True


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

    def report(self, messenger):
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



class Campaign (kxg.Token):

    def __init__(self, army, community):
        kxg.Token.__init__(self)

        self.army = army
        self.community = community

    @kxg.check_for_safety
    def setup(self):
        self.army.add_campaign(self)
        self.community.add_campaign(self)

    @kxg.check_for_safety
    def update(self, time):
        pass

    def report(self, messenger):
        if self.was_successful():
            army = self.army
            community = self.community

            assert not army.battle

            if community.battle:
                message = messages.JoinBattle(self, community.battle)
                messenger.send_message(message)
            else:
                message = messages.StartBattle(self)
                messenger.send_message(message)

    @kxg.check_for_safety
    def teardown(self):
        self.army.forget_campaign(self)
        self.community.forget_campaign(self)


    def was_successful(self):
        return self.army.check_engagement_proximity(self.community)

class Battle (kxg.Token):

    # Settings (fold)
    time_until_capture = 25

    def __init__(self, campaign):
        kxg.Token.__init__(self)

        self.init_campaign = campaign  # Will be deleted in setup
        self.communities = {}


    @kxg.check_for_safety
    def setup(self):
        campaign = self.init_campaign
        self.add_community(campaign.army)
        self.add_community(campaign.community)

        del self.init_campaign

    @kxg.check_for_safety
    def update(self, time):
        pass

    def report(self, messenger):
        pass
        #for player in self.communities.keys:
        #    if len(self.communities[player]) == 0:
        #        # remove player ??
        #if self.was_successful():
        #    message = messages.CaptureCity(self)
        #    self.send_message(message)

    @kxg.check_for_safety
    def teardown(self):
        for communities in self.communities.values():
            for community in communities:
                community.battle = None


    @kxg.check_for_safety
    def add_community(self, community):
        player = community.player
        if player not in self.communities:
            self.communities[player] = []
        self.communities[player].append(community)
        community.engage_battle(self)

    def get_initiation_price(self):
        pass

    def get_retreat_cost(self):
        pass

    def was_successful(self):
        return len(self.communities.keys) == 1


