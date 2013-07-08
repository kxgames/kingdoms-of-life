from __future__ import division

import kxg
import messages
import gui

class World (kxg.World):

    def __init__ (self):
        kxg.World.__init__(self)

        self.players = []
        self.losers = []; self.winner = None
        self.map = kxg.geometry.Rectangle.from_size(500, 500)

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
        city.player.add_city(city)
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
    def upgrade_community(self, community, price):
        community.upgrade()
        community.player.spend_wealth(price)

    @kxg.check_for_safety
    def destroy_army(self, army):
        # Removing army from battle.
        if army.battle:
            army.battle.remove_community(army)

        # Destroying any associated campaigns.
        if army.campaigns:
            for campaign in army.campaigns:
                campaign.teardown()
                self.remove_token(campaign)

        army.teardown()

        army.player.armies.remove(army)
        self.remove_token(army)


    @kxg.check_for_safety
    def request_battle(self, campaign):
        player = campaign.army.player
        price = campaign.community.get_battle_price()
        player.spend_wealth(price)

        self.add_token(campaign)
        campaign.setup()
        campaign.army.chase(campaign)

    @kxg.check_for_safety
    def start_battle(self, campaign, battle):

        if campaign.community.is_army():
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
    def retreat_battle(self, army, target):
        army.battle.retreat(army)
        army.exit_battle()
        army.move_to(target)

    @kxg.check_for_safety
    def zombify_city(self, battle, city):
        battle.zombify_city(city)

    @kxg.check_for_safety
    def end_battle(self, battle):
        city = battle.zombie_city
        if city:
            city.set_health_to_min()

            if battle.communities.keys():
                winner = battle.communities.keys()[0]
                if winner != city.player:
                    self.capture_city(city, winner)

        battle.teardown()
        self.remove_token(battle)

    @kxg.check_for_safety
    def capture_city(self, city, attacker):
        defender = city.player
        
        # Give control of the city to the attacker.
        city.player = attacker
        defender.cities.remove(city)
        attacker.cities.append(city)

        # Remove all the existing roads into this city.
        for road in defender.roads[:]:
            if road.has_terminus(city):
                defender.roads.remove(road)
                road.teardown()
                self.remove_token(road)


    @kxg.check_for_safety
    def old_attack_city(self, battle, price):
        self.add_token(battle)
        battle.attacker.battles.append(battle)
        battle.attacker.spend_wealth(price)
        battle.setup()

    @kxg.check_for_safety
    def old_defend_city(self, battle, price):
        battle.defender.spend_wealth(price)
        battle.attacker.battles.remove(battle)
        battle.teardown()
        self.remove_token(battle)

    @kxg.check_for_safety
    def old_capture_city(self, battle):
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
        player.dead = True
        self.losers.append(player)
        self.players.remove(player)
        player.teardown()
        #self.remove_token(player)
    

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

    def find_closest_community(self, target, player=None, cutoff=None):
        closest_distance = kxg.geometry.infinity
        closest_community = None

        if player is None:
            communities = self.yield_communities()
        else:
            communities = player.cities + player.armies

        for community in communities:
            offset = target - community.position
            distance = offset.magnitude

            if distance < closest_distance:
                closest_distance = distance
                closest_community = community

        if (cutoff is not None) and (closest_distance > cutoff):
            return None

        return closest_community


    def yield_cities(self):
        for player in self.players:
            for city in player.cities:
                yield city

    def yield_armies(self):
        for player in self.players:
            for army in player.armies:
                yield army

    def yield_communities(self):
        for player in self.players:
            for city in player.cities:
                yield city
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

    def upgrade_community(self, community, is_mine):
        assert not is_mine

    def destroy_army(self, army, is_mine):
        pass

    def request_battle(self, campaign, is_mine):
        assert not is_mine

    def start_battle(self, battle):
        pass

    def join_battle(self, battle):
        pass

    def retreat_battle(self, army, target, is_mine):
        assert not is_mine

    def zombify_city(self, battle, city, is_mine):
        pass

    def end_battle(self, battle, is_mine):
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

    def defeat_player(self):
        if len(self.world.players) == 1:
            winner = self.world.players[0]
            message = messages.GameOver(winner)
            self.send_message(message)


    def show_error(self, message):
        print message.error



class Player (kxg.Token):

    # Settings (fold)
    starting_wealth = 200
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
        self.played_city = False
        self.dead = False

        self.wealth = self.starting_wealth
        self.revenue = self.starting_revenue

    def __extend__(self):
        return {'gui': gui.PlayerExtension}


    @kxg.check_for_safety
    def setup(self, world):
        self.world = world

    @kxg.check_for_safety
    def update(self, time):
        self.revenue = self.starting_revenue

        for city in self.cities:
            self.revenue += city.get_revenue()

        for army in self.armies:
            self.revenue += army.get_revenue()

        for road in self.roads:
            self.revenue += road.get_revenue()

        self.wealth += time * self.revenue / 30

        for extension in self.get_extensions():
            extension.update_wealth()

    def report(self, messenger):
        if self.was_defeated() and not self.is_dead():
            message = messages.DefeatPlayer(self)
            messenger.send_message(message)

    @kxg.check_for_safety
    def teardown(self):
        for battle in self.battles:
            battle.remove_player(self)
        for token in self.cities + self.armies + self.roads:
            token.teardown()
            self.world.remove_token(token)
        self.cities = []
        self.armies = []
        self.roads = []
        self.battles = []


    @kxg.check_for_safety
    def add_city(self, city):
        self.cities.append(city)
        self.played_city = True

    @kxg.check_for_safety
    def remove_army(self, army):
        try:
            self.armies.remove(army)
        except ValueError:
            pass

    @kxg.check_for_safety
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

    def find_closest_community(self, target, cutoff=None):
        return self.world.find_closest_community(target, self, cutoff)
    
    def is_dead(self):
        return self.dead

    def was_defeated(self):
        return (not self.cities and self.played_city) or self.is_dead()


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


    @kxg.check_for_safety
    def update(self, time):
        if not self.battle:
            if self.health < self.get_max_health():
                self.heal(self.get_healing() * time)

        for extension in self.get_extensions():
            extension.update(time)


    @kxg.check_for_safety
    def upgrade(self):
        health_percent = self.health / self.get_max_health()
        self.level += 1
        self.health = health_percent * self.get_max_health()

        for extension in self.get_extensions():
            extension.update_level()

    @kxg.check_for_safety
    def damage(self, delta):
        self.health -= delta

        for extension in self.get_extensions():
            extension.update_health()

    @kxg.check_for_safety
    def heal(self, delta):
        self.health += delta

        if self.health > self.get_max_health():
            self.health = self.get_max_health()

        for extension in self.get_extensions():
            extension.update_health()

    @kxg.check_for_safety
    def add_campaign(self, campaign):
        self.campaigns.append(campaign)

    @kxg.check_for_safety
    def forget_campaign(self, campaign):
        raise NotImplementedError

    @kxg.check_for_safety
    def enter_battle(self, battle):
        self.battle = battle
        for extension in self.get_extensions():
            extension.update_engagement()

    @kxg.check_for_safety
    def exit_battle(self):
        self.battle = None
        for extension in self.get_extensions():
            extension.update_engagement()


    def get_level(self):
        return self.level

    def get_health(self):
        return self.health

    def get_max_health(self):
        raise NotImplementedError

    def get_healing(self):
        raise NotImplementedError

    def get_attack(self):
        raise NotImplementedError

    def get_supply(self):
        raise NotImplementedError

    def get_revenue(self):
        # Any community can generate revenue, but only cities can right now.
        return 0

    def can_move(self):
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

    def is_army(self):
        raise NotImplementedError

    def is_city(self):
        raise NotImplementedError


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
        Community.update(self, time)

    def report(self, messenger):
        if self.health <= 0:
            if self.battle:
                if self.battle.zombie_city != self:
                    message = messages.ZombifyCity(self)
                    messenger.send_message(message)
            else:
                raise NotImplementedError

    @kxg.check_for_safety
    def teardown(self):
        raise AssertionError


    @kxg.check_for_safety
    def forget_campaign(self, campaign):
        try:
            self.campaigns.remove(campaign)
        except ValueError:
            pass

    @kxg.check_for_safety
    def set_health_to_min(self):
        if self.health <= 1:
            self.health = 1


    def get_price(self):
        return 20 + 10 * len(self.player.cities)

    def get_upgrade_price(self):
        return 10 * self.level

    def get_max_health(self):
        return 80 + 20 * self.level

    def get_revenue(self):
        clear_roads = sum(1 for road in self.roads if not road.is_blocked())
        return 5 * self.level + 10 * clear_roads

    def get_healing(self):
        return 2 * self.level

    def get_attack(self):
        return 2 + self.level // 2

    def get_supply(self):
        return sum((road.get_supply_to(self) for road in self.roads), 1)
    
    def get_battle_price(self):
        return 100

    def can_move(self):
        return False

    def is_army(self):
        return False

    def is_city(self):
        return True


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
        Community.update(self, time)

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

                for extension in self.get_extensions():
                    extension.update_position()

    def report(self, messenger):
        if self.health <= 0:
            message = messages.DestroyArmy(self)
            messenger.send_message(message)

    @kxg.check_for_safety
    def teardown(self):
        for extension in self.get_extensions():
            extension.teardown()


    @kxg.check_for_safety
    def chase (self, campaign):
        self.my_campaign = campaign

    @kxg.check_for_safety
    def forget_campaign(self, campaign):
        if campaign:
            try:
                self.campaigns.remove(campaign)
            except ValueError:
                pass

            if self.my_campaign is campaign:
                self.my_campaign = None
                self.target = None
        
    @kxg.check_for_safety
    def enter_battle(self, battle):
        Community.enter_battle(self, battle)
        self.target = None
        self.forget_campaign(self.my_campaign)

    @kxg.check_for_safety
    def move_to(self, target):
        self.target = target
        for extension in self.get_extensions():
            extension.update_target()


    def get_price(self):
        return 30 + 10 * len(self.player.armies)

    def get_upgrade_price(self):
        return 10 * self.level

    def get_max_health(self):
        return 60 + 16 * self.level

    def get_healing(self):
        return self.level

    def get_attack(self):
        return 4 + 2 * self.level

    def get_supply(self):
        city_supplies = []

        for city in self.player.cities:
            city_supply = city.get_supply()
            city_supplies.append(city_supply)

        return max(city_supplies)

    def get_battle_price(self):
        return 0

    def can_move(self):
        return True

    def can_move_to(self, position):
        return True

    def can_request_battle(self, community):
        return True


    def is_army(self):
        return True

    def is_city(self):
        return False


class Road (kxg.Token):

    def __init__(self, player, start, end):
        kxg.Token.__init__(self)
        self.player = player
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.start
        yield self.end

    def __extend__(self):
        return {'gui': gui.RoadExtension}


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

        for extension in self.get_extensions():
            extension.teardown()


    def get_price(self):
        return 20 + 10 * len(self.player.roads)

    def get_revenue(self):
        # Revenue is currently generated by cities only, not roads.  But this 
        # method is being kept in the codebase to make it easy to add revenue 
        # to roads in the future.
        return 0

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

    def is_blocked(self):
        return self.start.is_in_battle() or self.end.is_in_battle()



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

            print army.battle
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
        self.zombie_city = None


    @kxg.check_for_safety
    def setup(self):
        campaign = self.init_campaign
        self.add_community(campaign.army)
        self.add_community(campaign.community)

        del self.init_campaign

    @kxg.check_for_safety
    def update(self, time):
        cats = self.communities

        cat_count = 0
        for player in cats:
            cat_count += len(cats[player])

        for player in cats:
            enemy_count = cat_count - len(cats[player])
            player_attack_total = 0
            for cat in cats[player]:
                player_attack_total += cat.get_attack()

            per_cat_damage = player_attack_total * time / cat_count

            for enemy in cats:
                if enemy is player:
                    continue
                for cat in cats[enemy]:
                    cat.damage(per_cat_damage)
            

    def report(self, messenger):
        if self.was_successful():
            message = messages.EndBattle(self)
            messenger.send_message(message)

    @kxg.check_for_safety
    def teardown(self):
        if self.zombie_city:
            self.zombie_city.battle = None
            self.zombie_city.exit_battle()
        for communities in self.communities.values():
            for community in communities:
                community.exit_battle()


    @kxg.check_for_safety
    def retreat(self, army):
        self.remove_community (army)

    @kxg.check_for_safety
    def zombify_city(self, city):
        player = city.player

        self.zombie_city = city

        self.communities[player].remove(city)
        if not self.communities[player]:
            del self.communities[player]

    @kxg.check_for_safety
    def remove_community(self, community):
        player = community.player

        community.battle = None

        self.communities[player].remove(community)
        if not self.communities[player]:
            del self.communities[player]

    @kxg.check_for_safety
    def add_community(self, community):
        player = community.player
        if player not in self.communities:
            self.communities[player] = []
        self.communities[player].append(community)
        community.enter_battle(self)

    @kxg.check_for_safety
    def remove_player(self, player):
        if player in self.communities:
            for community in self.communities[player]:
                community.battle = None
            del self.communities[player]


    def get_initiation_price(self):
        pass

    def get_retreat_battle_price(self):
        return 50

    def get_zombie_city(self):
        return self.zombie_city

    def was_successful(self):
        return len(self.communities.keys()) <= 1


