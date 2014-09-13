import kxg, vecrec, networkx, itertools
import messages, helpers, gui, arguments

class World (kxg.World):

    def __init__ (self):
        kxg.World.__init__(self)

        self.map = None
        self.players = []
        self.winner = None
        self.losers = []

        self.game_started = False
        self.game_ended = False
        self.elapsed_time = 0

    def update(self, time):
        self.elapsed_time += time

    def start_game(self, map):
        self.game_started = True
        self.map = self.add_token(map)

    def game_over(self, winner):
        self.game_ended = True
        self.winner = winner

    @kxg.read_only
    def has_game_started (self):
        return self.game_started

    @kxg.read_only
    def has_game_ended (self):
        return self.game_ended


    def create_player(self, player):
        self.add_token(player, self.players)
        player.set_world(self)

    def create_city(self, city, price):
        self.add_token(city)
        city.player.add_city(city)
        city.player.spend_wealth(price)

    def create_army(self, army, price):
        self.add_token(army, army.player.armies)
        army.player.spend_wealth(price)

    def create_road(self, road, price):
        self.add_token(road, road.player.roads)
        road.player.spend_wealth(price)

    def upgrade_community(self, community, price):
        community.upgrade()
        community.player.spend_wealth(price)

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


    def request_battle(self, campaign):
        player = campaign.army.player
        # Pay to start a battle.
        if not campaign.community.is_in_battle():
            price = campaign.army.get_battle_price()
            player.spend_wealth(price)

        self.add_token(campaign)
        campaign.army.chase(campaign)

    def start_battle(self, campaign, battle):
        if campaign.community.is_army():
            cancelled_campaign = campaign.community.my_campaign
            if cancelled_campaign:
                cancelled_campaign.teardown()
                self.remove_token(cancelled_campaign)

        campaign.teardown()
        self.remove_token(campaign)
        self.add_token(battle)

    def join_battle(self, campaign, battle):
        battle.add_community(campaign.army)

        campaign.teardown()
        self.remove_token(campaign)

    def retreat_battle(self, army, price):
        army.player.spend_wealth(price)

        if army.battle:
            army.battle.retreat(army)
            army.exit_battle()
        else:
            campaign = army.my_campaign
            campaign.teardown()
            self.remove_token(campaign)

    def reinforce_community(self, community):
        bonus = community.get_reinforce_bonus()
        price = community.get_reinforce_price()

        community.player.spend_wealth(price)
        community.heal(bonus)

    def zombify_city(self, battle, city):
        battle.zombify_city(city)

    def end_battle(self, battle):
        city = battle.get_zombie_city()
        winner = None
        if battle.communities.keys():
            winner = battle.communities.keys()[0]
            winner.gain_wealth(battle.get_plunder())

        if city:
            city.set_health_to_min()
            if winner != city.player:
                self.capture_city(city, winner)

        battle.teardown()
        self.remove_token(battle)

    def capture_city(self, city, attacker):
        defender = city.player
        
        # Give control of the city to the attacker.
        defender.lose_city(city)
        attacker.add_city(city)

        # Remove all the existing roads into this city.
        for road in defender.roads[:]:
            if road.has_terminus(city):
                defender.roads.remove(road)
                road.teardown()
                self.remove_token(road)


    def defeat_player(self, player):
        player.dead = True
        self.losers.append(player)
        self.players.remove(player)
        player.teardown()
    

    @kxg.read_only
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

    @kxg.read_only
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

    @kxg.read_only
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


    @kxg.read_only
    def yield_cities(self):
        for player in self.players:
            for city in player.cities:
                yield city

    @kxg.read_only
    def yield_armies(self):
        for player in self.players:
            for army in player.armies:
                yield army

    @kxg.read_only
    def yield_communities(self):
        for player in self.players:
            for city in player.cities:
                yield city
            for army in player.armies:
                yield army

    @kxg.read_only
    def yield_roads(self):
        for player in self.players:
            for road in player.roads:
                yield road

    @kxg.read_only
    def yield_battles(self):
        for player in self.players:
            for battle in player.battle:
                yield battle


class Referee (kxg.Referee):

    def __init__(self):
        kxg.Referee.__init__(self)
        self.world = None
        self.frame = 0

    def get_name(self):
        return 'referee'


    def setup(self, world):
        kxg.Referee.setup(self, world)
        message = messages.StartGame()
        self.send_message(message)

    def update(self, time):
        kxg.Referee.update(self, time)
        self.frame += 1

    def teardown(self):
        pass


    def show_error(self, message):
        print(message.error)


class Player (kxg.Token):

    # Settings (fold)
    starting_wealth = 200
    starting_revenue = 25
    

    def __init__(self, name, color):
        kxg.Token.__init__(self)

        self.name = name
        self.color = color
        self.world = None
        self.capitol = None
        self.cities = []
        self.armies = []
        self.roads = []
        self.battles = []
        self.played_city = False
        self.dead = False

        self.wealth = self.starting_wealth
        self.revenue = self.starting_revenue
        
        if arguments.wealthy:
            self.wealth = 10000

    def __extend__(self):
        return {}

    def __str__(self):
        return '<Player name=%s>' % self.name


    def setup(self, world):
        pass

    def update(self, time):
        self.revenue = self.starting_revenue

        for city in self.cities:
            self.revenue += city.get_revenue()
        
        self.wealth += time * self.revenue / 30

        for extension in self.get_extensions():
            extension.update_wealth()
            extension.update_costs()

    @kxg.read_only
    def report(self, messenger):
        if self.was_defeated() and not self.is_dead():
            message = messages.DefeatPlayer(self)
            messenger.send_message(message)

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


    def set_world(self, world):
        self.world = world

    @kxg.before_setup
    def set_actor(self, id):
        self.actor = id

    def add_city(self, city):
        city.player = self
        if not self.cities:
            self.capitol = city
            self.capitol.update_capitol()
            self.played_city = True
        self.cities.append(city)

    def lose_city(self, city):
        city.player = None
        self.cities.remove(city)

        if city is self.capitol:
            city.update_capitol()

            if self.cities:
                self.capitol = self.cities[0]
                self.capitol.update_capitol()

    def remove_army(self, army):
        try:
            self.armies.remove(army)
        except ValueError:
            pass

    def spend_wealth(self, price):
        self.wealth -= price

    def gain_wealth(self, amount):
        self.wealth += amount


    @kxg.read_only
    def get_supply(self, resource):
        return sum(city.get_supply(resource) for city in self.cities)


    @kxg.read_only
    def get_city_price(self):
        return 40 + 5 * len(self.cities)

    @kxg.read_only
    def get_army_price(self):
        return 50 + 100 * len(self.armies)

    @kxg.read_only
    def get_road_price(self):
        return 30 + 15 * len(self.roads)


    @kxg.read_only
    def can_afford_price(self, price):
        return price <= self.wealth

    @kxg.read_only
    def inside_territory(self, community):
        inside_border = False
        inside_opponent = False

        for other in self.world.yield_cities():
            offset = community.position - other.position
            distance = offset.magnitude

            if other.player is self:
                inside_border = (distance <= other.border) or inside_border
            else:
                inside_opponent = (distance <= other.border) or inside_opponent 

        if inside_opponent:
            return False

        if not inside_border:
            return False

        return True

    @kxg.read_only
    def can_see(self, target):
        # Cities are always visible through the fog-of-war.
        if target.is_city():
            return True

        # Armies are only visible if they are within some radius of a city or 
        # army controlled by the player.
        for community in self.cities + self.armies:
            distance = community.position.get_distance(target.position) - 40
            line_of_sight = community.get_line_of_sight() 

            if distance <= line_of_sight:
                return True

        return False

    @kxg.read_only
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

    @kxg.read_only
    def can_place_army(self, army):
        inside_border = False
        inside_opponent = False

        for other in self.world.yield_communities():
            offset = army.position - other.position
            distance = offset.magnitude

            if distance <= 2 * other.radius:
                return False

        for other in self.world.yield_cities():
            offset = army.position - other.position
            distance = offset.magnitude

            if other.player is self:
                inside_border = (distance <= other.border) or inside_border
            else:
                inside_opponent = (distance <= other.border) or inside_opponent 

        if inside_opponent:
            return False

        if not inside_border:
            return False

        return True

    @kxg.read_only
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

    @kxg.read_only
    def find_closest_city(self, target, cutoff=None):
        return self.world.find_closest_city(target, self, cutoff)

    @kxg.read_only
    def find_closest_army(self, target, cutoff=None):
        return self.world.find_closest_army(target, self, cutoff)

    @kxg.read_only
    def find_closest_community(self, target, cutoff=None):
        return self.world.find_closest_community(target, self, cutoff)
    
    @kxg.read_only
    def get_capitol(self):
        return self.capitol

    @kxg.read_only
    def is_dead(self):
        return self.dead

    @kxg.read_only
    def was_defeated(self):
        return (not self.cities and self.played_city) or self.is_dead()


class Map (kxg.Token):

    terrains = {    # (fold)
            (0, 255, 0): 'land',
            (0, 0, 255): 'sea'
    }

    resources = (   # (fold)
            'spiral',
            'wheel',
            'quarter',
            'oculus',
            'moon',
    )


    def __init__(self, path):
        kxg.Token.__init__(self)
        self.path = path
        self.tiles = {}
        self.graphs = {}
        self.resource_tiles = set()
        self.rows, self.columns = 0, 0

    def __str__(self):
        return '<Map w={} h={}>'.format(self.columns, self.rows)

    def __getitem__(self, index):
        return self.tiles[index]

    def setup(self, world):
        self.setup_tiles()
        self.setup_graphs()
        self.setup_resources()

    def setup_tiles(self):
        from PIL import Image

        image = Image.open(self.path)
        self.columns, self.rows = image.size

        for row, col in self.yield_indices():
            pixel = image.getpixel((col, row))
            terrain = Map.terrains[pixel]
            self.tiles[row, col] = Tile(row, col, terrain)
    
    def setup_graphs(self):
        # Connect the tiles into graph structures that can easily be searched 
        # (for shortest paths and so forth).  Two graphs are currently created: 
        # one with all the land tiles and another with all the sea tiles.  This 
        # makes it possible to find paths for both land and sea units.  More 
        # graphs may be necessary as we add units that move in different ways.

        self.graphs = {
                'land': networkx.Graph(),
                'sea': networkx.Graph()
        }

        # Fill each graphs with the appropriate tiles.

        for tile in self.yield_tiles():
            if tile.is_land: self.graphs['land'].add_node(tile)
            if tile.is_sea: self.graphs['sea'].add_node(tile)

        # Create edges for all the graphs.  Diagonal edges are included.

        half_neighbors = lambda row, col: [
                        (row + 1, col + 0),
                        (row + 1, col + 1),
                        (row + 0, col + 1),
                        (row - 1, col + 1) ]

        for row_1, col_1 in self.yield_indices():
            index_1 = row_1, col_1
            tile_1 = self.tiles[index_1]

            for row_2, col_2 in half_neighbors(row_1, col_1):
                index_2 = row_2, col_2
                tile_2 = self.tiles.get(index_2)

                if tile_2 is None:
                    continue

                weight = vecrec.get_distance(index_1, index_2)

                if tile_1.is_land and tile_2.is_land:
                    self.graphs['land'].add_edge(tile_1, tile_2, weight=weight)

                if tile_1.is_sea and tile_2.is_sea:
                    self.graphs['sea'].add_edge(tile_1, tile_2, weight=weight)

    def setup_resources(self):
        import random

        num_resources = 40
        resource_spacing = 20
        tile_list = list(self.tiles.values())

        def location_ok(tile):
            if not tile.is_land: return False

            # Require that the tile and all it's neighbors are land.

            for neighbor in self.yield_neighbors(tile):
                if not neighbor.is_land: return False

            # Require that there's no other resource within some radius.
            
            min_distance = float('inf')

            for resource_tile in self.resource_tiles:
                distance = vecrec.get_distance(tile.index, resource_tile.index)
                min_distance = min(distance, min_distance)
                if min_distance < resource_spacing: return False

            # If resource looks good, add it to the map.

            return True

        while len(self.resource_tiles) < num_resources:
            tile = random.choice(tile_list)

            if location_ok(tile):
                tile.resource = random.choice(self.resources)
                self.resource_tiles.add(tile)

        for tile in self.resource_tiles:
            print(tile)

    def find_path(self, source, target, graph='land'):
        from networkx.algorithms.shortest_paths import astar_path
        return astar_path(
                self.graphs[graph], source, target, self.a_star_heuristic)

    def find_path_distance(self, source, target, graph='land'):
        from networkx.algorithms.shortest_paths import astar_path_length
        return astar_path_length(
                self.graphs[graph], source, target, self.a_star_heuristic)

    @staticmethod
    def a_star_heuristic(a, b):
        return vecrec.get_distance(a.index, b.index)

    def yield_indices(self):
        return itertools.product(range(self.rows), range(self.columns))

    def yield_tiles(self):
        return iter(self.tiles.values())

    def yield_neighbors(self, tile):
        row, col = tile.index

        neighbors = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
        ]
        for index in neighbors:
            tile = self.tiles.get(index)
            if tile is not None: yield tile


class Tile:

    def __init__(self, row, col, terrain):
        self.row, self.col = row, col
        self.terrain = terrain
        self.resource = None
    
    def __str__(self):
        msg = '<Tile row={0.row} col={0.col} terrain={0.terrain}'
        if self.resource is not None: msg += ' resource={0.resource}'
        msg += '>'
        return msg.format(self)

    def __eq__(self, other):
        # No two tiles should have the same index.
        return self.index == other.index

    def __hash__(self):
        # No two tiles should have the same index.
        return hash(self.index)

    @property
    def index(self):
        return self.row, self.col

    @property
    def is_land(self):
        return self.terrain == 'land'

    @property
    def is_sea(self):
        return self.terrain == 'sea'


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


    def setup(self, world):
        self.world = world

    def update(self, time):
        if not self.battle:
            if self.health < self.get_max_health():
                self.heal(self.get_healing() * time)

        for extension in self.get_extensions():
            extension.update(time)


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

    def heal(self, delta):
        self.health += delta

        if self.health > self.get_max_health():
            self.health = self.get_max_health()

        for extension in self.get_extensions():
            extension.update_health()

    def add_campaign(self, campaign):
        self.campaigns.append(campaign)

    def forget_campaign(self, campaign):
        raise NotImplementedError

    def enter_battle(self, battle):
        self.battle = battle
        for extension in self.get_extensions():
            extension.update_engagement()

    def exit_battle(self):
        self.battle = None
        for extension in self.get_extensions():
            extension.update_engagement()


    @kxg.read_only
    def get_position(self):
        return self.position

    @kxg.read_only
    def get_level(self):
        return self.level

    @kxg.read_only
    def get_health(self):
        return self.health

    @kxg.read_only
    def get_max_health(self):
        raise NotImplementedError

    @kxg.read_only
    def get_healing(self):
        raise NotImplementedError

    @kxg.read_only
    def get_attack(self):
        raise NotImplementedError

    @kxg.read_only
    def get_supply(self):
        raise NotImplementedError

    @kxg.read_only
    def get_revenue(self):
        # Any community can generate revenue, but only cities can right now.
        return 0

    @kxg.read_only
    def get_reinforce_price(self):
        return 20

    @kxg.read_only
    def get_reinforce_bonus(self):
        return 5

    @kxg.read_only
    def get_line_of_sight(self):
        raise NotImplementedError

    @kxg.read_only
    def can_move(self):
        raise NotImplementedError

    @kxg.read_only
    def get_distance_to(self, other):
        return self.position.get_distance(other.position)

    @kxg.read_only
    def check_battle_proximity(self, battle):
        communities = battle.communities
        for player in battle.communities.keys():
            if self.player is not player:
                for community in communities[player]:
                    if self.check_engagement_proximity(community):
                        return True
        return False

    @kxg.read_only
    def check_engagement_proximity(self, community):
        radius = self.radius + community.radius + self.engagement_range
        distance = community.position - self.position
        
        return radius >= distance.magnitude


    @kxg.read_only
    def inside_friendly_territory(self):
        return self.player.inside_territory(self)

    @kxg.read_only
    def is_in_battle(self):
        return self.battle is not None

    @kxg.read_only
    def is_army(self):
        raise NotImplementedError

    @kxg.read_only
    def is_city(self):
        raise NotImplementedError


class City (Community):

    # Settings (fold)
    buffer = 90
    border = 130

    def __init__(self, player, position):
        Community.__init__(self, player, position)
        self.resources = {}
        self.investments = {}
        self.roads = []

    def __extend__(self):
        return {}

    def __str__(self):
        return '<City id=%s xy=%s>' % (self.get_id(), self.position)


    def setup(self, world):
        Community.setup(self, world)

    def update(self, time):
        Community.update(self, time)

    @kxg.read_only
    def report(self, messenger):
        if self.health <= 0:
            if self.battle:
                if self.battle.zombie_city != self:
                    message = messages.ZombifyCity(self)
                    messenger.send_message(message)
            else:
                raise NotImplementedError

    def teardown(self):
        raise AssertionError


    def forget_campaign(self, campaign):
        try:
            self.campaigns.remove(campaign)
        except ValueError:
            pass

        for extension in self.get_extensions():
            extension.update_engagement()

    def set_health_to_min(self):
        if self.health <= 1:
            self.health = 1

    def update_capitol(self):
        for extension in self.get_extensions():
            extension.update_capitol()


    @kxg.read_only
    def get_upgrade_price(self):
        return 40 * self.level

    @kxg.read_only
    def get_max_health(self):
        return 150 + 30 * self.level

    @kxg.read_only
    def get_supply(self, resource):
        from math import exp
        diminishing_returns = lambda x: 1 - exp(-x)
        resource = self.resources.get(resource, 0)
        investment = 0.5 + self.investments.get(resource, 0)
        return resource * diminishing_returns(investment)

    @kxg.read_only
    def get_revenue(self):
        """ Return the revenue generated by this city.  The revenue depends on 
        three factors: the global demand, the amount of raw material in the 
        city, and the amount the city has invested in that resource.  The 
        return on investment in each resource diminishes exponentially. """

        revenue = 0

        for resource in self.resources:
            demand = self.world.get_demand(resource)
            supply = self.get_supply(resource)
            revenue += demand * supply

        return revenue

    @kxg.read_only
    def get_healing(self):
        capitol = self.player.get_capitol()
        radius = self.radius

        distance = self.get_distance_to(capitol)
        a = - 1.0 / (3 * radius)
        max_rate = 2 * self.level
        rate = a * (distance - 2 * radius) + max_rate

        baseline = 1
        if rate <= baseline:
            return baseline
        elif rate >= max_rate:
            return max_rate
        else:
            return rate

    @kxg.read_only
    def get_attack(self):
        return 2 + self.level // 2

    @kxg.read_only
    def get_maximum_level(self):
        return 9

    @kxg.read_only
    def get_line_of_sight(self):
        return self.border + 30

    @kxg.read_only
    def can_move(self):
        return False

    @kxg.read_only
    def is_army(self):
        return False

    @kxg.read_only
    def is_city(self):
        return True

    @kxg.read_only
    def is_capitol(self):
        return self.player and self.player.capitol is self


class Army (Community):

    # Settings (fold)
    speed = 25

    def __init__(self, player, position):
        Community.__init__(self, player, position)

        self.my_campaign = None
        self.target = None

    def __extend__(self):
        return {}

    def __str__(self):
        return "<Army id=%s>" % self.get_id()


    def setup(self, world):
        Community.setup(self, world)

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

    @kxg.read_only
    def report(self, messenger):
        if self.health <= 0:
            message = messages.DestroyArmy(self)
            messenger.send_message(message)

    def teardown(self):
        for extension in self.get_extensions():
            extension.teardown()


    def chase(self, campaign):
        self.my_campaign = campaign
        for extension in self.get_extensions():
            extension.update_engagement()

    def forget_campaign(self, campaign):
        if campaign:
            try:
                self.campaigns.remove(campaign)
            except ValueError:
                pass

            if self.my_campaign is campaign:
                self.my_campaign = None
                self.target = None

        for extension in self.get_extensions():
            extension.update_engagement()
        
    def enter_battle(self, battle):
        Community.enter_battle(self, battle)
        self.target = None
        self.forget_campaign(self.my_campaign)

    def move_to(self, target):
        self.target = target
        for extension in self.get_extensions():
            extension.update_target()


    @kxg.read_only
    def get_upgrade_price(self):
        return 83 * self.level - 33

    @kxg.read_only
    def get_max_health(self):
        return 150 + 30 * self.level

    @kxg.read_only
    def get_healing(self):
        capitol = self.player.get_capitol()
        radius = self.radius

        distance = self.get_distance_to(capitol)
        a = - 1.0 / (3 * radius)
        max_rate = 2 * self.level
        rate = a * (distance - 2 * radius) + max_rate

        baseline = 1
        if rate <= baseline:
            return baseline
        elif rate >= max_rate:
            return max_rate
        else:
            return rate

    @kxg.read_only
    def get_attack(self):
        level = self.level + 1 if self.inside_friendly_territory() else self.level
        return 2 + 3 * level

    @kxg.read_only
    def get_battle_price(self):
        return 0

    @kxg.read_only
    def get_retreat_price(self):
        # Campaigns can be retreated for free.
        return 70 if self.is_in_battle() else 0

    @kxg.read_only
    def get_maximum_level(self):
        return 5

    @kxg.read_only
    def get_line_of_sight(self):
        return 150

    @kxg.read_only
    def get_campaign(self):
        return self.my_campaign
    
    @kxg.read_only
    def can_move(self):
        return True

    @kxg.read_only
    def can_move_to(self, position):
        return True

    @kxg.read_only
    def can_request_battle(self, community):
        return True


    @kxg.read_only
    def is_chasing(self):
        return self.my_campaign is not None

    @kxg.read_only
    def is_army(self):
        return True

    @kxg.read_only
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
        return {}

    def __str__(self):
        return "<Road id=%s>" % self.get_id()


    def setup(self, world):
        self.world = world
        self.start.roads.append(self)
        self.end.roads.append(self)

    def update(self, time):
        pass

    def report(self, messenger):
        pass

    def teardown(self):
        self.start.roads.remove(self)
        self.end.roads.remove(self)

        for extension in self.get_extensions():
            extension.teardown()


    @kxg.read_only
    def get_revenue(self):
        # Revenue is currently generated by cities only, not roads.  But this 
        # method is being kept in the codebase to make it easy to add revenue 
        # to roads in the future.
        return 0

    @kxg.read_only
    def get_supply_to(self, city):
        assert self.has_terminus(city)

        if self.is_blocked():
            return 0

        if city is self.start:
            return self.end.level

        if city is self.end:
            return self.start.level

    @kxg.read_only
    def has_same_route(self, other):
        forwards =  (other.start is self.start and other.end is self.end)
        backwards = (other.start is self.end   and other.end is self.start)
        return forwards or backwards

    @kxg.read_only
    def has_terminus(self, city):
        return (self.start is city) or (self.end is city)

    @kxg.read_only
    def is_blocked(self):
        return self.start.is_in_battle() or self.end.is_in_battle()


class Campaign (kxg.Token):

    def __init__(self, army, community):
        kxg.Token.__init__(self)

        self.army = army
        self.community = community

    def __str__(self):
        return '<Campaign id=%s>' % self.get_id()

    def setup(self, world):
        self.world = world
        self.army.add_campaign(self)
        self.community.add_campaign(self)

    def update(self, time):
        pass

    @kxg.read_only
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

    def teardown(self):
        self.army.forget_campaign(self)
        self.community.forget_campaign(self)


    @kxg.read_only
    def get_army(self):
        return self.army

    @kxg.read_only
    def get_community(self):
        return self.community


    @kxg.read_only
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
        self.plunder = 0

    def __str__(self):
        return "<Battle id=%s>" % self.get_id()


    def setup(self, world):
        self.world = world
        self.add_community(self.init_campaign.army)
        self.add_community(self.init_campaign.community)
        del self.init_campaign

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
            

    @kxg.read_only
    def report(self, messenger):
        if self.was_successful():
            message = messages.EndBattle(self)
            messenger.send_message(message)

    def teardown(self):
        if self.zombie_city:
            self.zombie_city.battle = None
            self.zombie_city.exit_battle()
        for communities in self.communities.values():
            for community in communities:
                community.exit_battle()


    def retreat(self, army):
        self.remove_community(army)

    def zombify_city(self, city):
        player = city.player

        self.zombie_city = city

        self.communities[player].remove(city)
        if not self.communities[player]:
            del self.communities[player]

    def remove_community(self, community):
        player = community.player

        community.battle = None

        self.communities[player].remove(community)
        if not self.communities[player]:
            del self.communities[player]

    def add_community(self, community):
        player = community.player
        if player not in self.communities:
            self.communities[player] = []
        self.communities[player].append(community)
        community.enter_battle(self)

        self.plunder += self.get_plunder_rate()

    def remove_player(self, player):
        if player in self.communities:
            for community in self.communities[player]:
                community.battle = None
            del self.communities[player]


    @kxg.read_only
    def get_initiation_price(self):
        pass

    @kxg.read_only
    def get_retreat_battle_price(self):
        return 50

    @kxg.read_only
    def get_plunder_rate(self):
        return 15

    @kxg.read_only
    def get_plunder(self):
        return self.plunder

    @kxg.read_only
    def get_zombie_city(self):
        return self.zombie_city

    @kxg.read_only
    def was_successful(self):
        return len(self.communities.keys()) <= 1



