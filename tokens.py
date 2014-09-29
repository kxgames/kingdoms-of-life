#!/usr/bin/env python3

import kxg, vecrec, networkx, itertools
import messages, helpers, gui, arguments

class World (kxg.World):

    def __init__ (self):
        kxg.World.__init__(self)

        self.map = None
        self.players = []
        self.winner = None
        self.losers = []
        self.families = []
        self.miracles = []
        self.game_started = False
        self.game_ended = False

    def update(self, time):
        for family in self.families:
            family.update(time)

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

    def create_family(self, family):
        self.add_token(family, family.player.families)

    def defeat_player(self, player):
        player.dead = True
        self.losers.append(player)
        self.players.remove(player)
        player.teardown()
    

class Referee (kxg.Referee):

    def __init__(self):
        kxg.Referee.__init__(self)
        self.world = None

    def get_name(self):
        return 'referee'

    def setup(self, world):
        kxg.Referee.setup(self, world)
        message = messages.StartGame()
        self.send_message(message)

    def update(self, time):
        kxg.Referee.update(self, time)

    def teardown(self):
        pass


class Player (kxg.Token):

    def __init__(self, name, color):
        kxg.Token.__init__(self)

        self.name = name
        self.color = color
        self.world = None

        self.families = []

    def __extend__(self):
        return {}

    def __str__(self):
        return '<Player name=%s>' % self.name

    def setup(self, world):
        pass

    def update(self, time):
        pass

    @kxg.read_only
    def report(self, messenger):
        if self.was_defeated() and not self.is_dead():
            message = messages.DefeatPlayer(self)
            messenger.send_message(message)

    def teardown(self):
        pass

    @kxg.before_setup
    def set_actor(self, id):
        self.actor = id

    @kxg.read_only
    def is_dead(self):
        return self.dead

    @kxg.read_only
    def was_defeated(self):
        return False


class Map (kxg.Token):

    climates = {    # (fold)
            (  0,   0, 255): 'water',
            (100,  50,   0): 'dirt',
            (  0, 255,   0): 'grass',
            (255, 255,   0): 'desert',
            (255, 255, 255): 'tundra',
    }


    def __init__(self, path):
        kxg.Token.__init__(self)
        self.path = path
        self.tiles = {}
        self.graphs = {}
        self.rows, self.columns = 0, 0

    def __extend__(self):
        return {gui.Gui: gui.MapExtension}

    def __str__(self):
        return '<Map w={} h={}>'.format(self.columns, self.rows)

    def __getitem__(self, index):
        # index is (row, col)
        # y, x ~ row, col
        return self.tiles[index]

    def setup(self, world):
        self.setup_tiles()
        self.setup_graphs()

    def setup_tiles(self):
        from PIL import Image

        image = Image.open(self.path)
        self.columns, self.rows = image.size

        for row, col in self.yield_indices():
            pixel = image.getpixel((col, row))
            climate = Map.climates[pixel]
            self.tiles[row, col] = Tile(row, col, climate)
    
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

    @property
    def land_tiles(self):
        return self.graphs['land'].nodes()


class Tile:

    def __init__(self, row, col, climate):
        self.row, self.col = row, col
        self.climate = climate
        self.families = {}
    
    def __str__(self):
        msg = '<Tile row={0.row} col={0.col} climate={0.climate}>'
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
        return self.climate != 'water'

    @property
    def is_sea(self):
        return self.climate == 'water'


class Family (kxg.Token):

    def __init__(self, player, name):
        super(Family, self).__init__()
        self.player = player
        self.name = name
        self.map = None

    def __extend__(self):
        return {gui.Gui: gui.FamilyExtension}

    def setup(self, world):
        self.map = world.map

    def get_tiles_occupied(self):
        return [x for x in self.map.land_tiles if self in x.families]

    def get_num_tiles_occupied(self):
        return len(self.get_tiles_occupied())

    def get_mean_position(self):
        position_sum = 0
        population_sum = 0

        for tile in self.map.land_tiles:
            population = tile.families.get(self, 0)
            position_sum += population * vecrec.Vector(*tile.index)
            population_sum += population

        return position_sum / population_sum

