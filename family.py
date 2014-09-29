import traits
import population


class Family:

    def __init__(self):

        # Universal traits
        self.piety = traits.ValueTrait()
        self.fecundity = traits.NormalizedTrait(.1)
        self.adaptability = traits.NormalizedTrait()
        self.temperature_tolerance = traits.GaussTrait()
        self.humidity_tolerance = traits.GaussTrait()

    def setup(self):
        pass

    def update(self, tile):
        # Called by the map on a tile by tile basis.
        #
        # In general families should:
        # 1. account for tile conditions
        # 2. identify amount of food
        # 3. change population
        # 4. spread to neighboring tiles
        # 5. Evolve!
        raise NotImplementedError

    def split(self):
        raise NotImplementedError


class Animal(Family):

    def __init__(self):
        Family.__init__(self)

        # Animal traits
        self.size = traits.ValueTrait()
        self.speed = traits.ValueTrait()
        self.intelligence = traits.ValueTrait()
        self.curiosity = traits.NormalizedTrait()
        self.carniverous = traits.NormalizedTrait()
        self.herbivorous = traits.NormalizedTrait()

class Plant(Family):

    def __init__(self):
        Family.__init__(self)

        # Plant traits
        self.height = traits.ValueTrait()
        self.established = traits.NormalizedTrait()
        self.invasiveness = traits.NormalizedTrait()

    def update(self, tile):
        population_size = tile.get_population(self)
        
        # 1. account for tile conditions

        # 2. identify amount of food
        insolation = tile.get_insolation(True, self.height)
        food_produced = insolation * population_size
        food_needed = population_size * self.height()**2

        food_ratio = food_produced / food_needed - 1

        # 3. change population
        population_delta = int(food_ratio * population_size * self.invasiveness())
        tile.add_population(self, population_delta)

        # 4. spread to neighboring tiles
        self.spread(tile)

        # 5. Evolve!

    def spread(self, tile):
        # Plants don't migrate (except coconuts). They send seeds which 
        # make new plants. Therefore, increase adjacent's population 
        # without decreasing this tile's population.
        
        population_size = tile.get_population(self)
        
        def calculate_offspring():
            # Calculate the population invading a neighboring tile.
            # Future: Account for shadiness of adjacent tile?
            #         ie. seeds fail to mature into adult plants
            # Future: Or instead of shadiness, use the established 
            # values of that tile...
            fecundity = random.uniform(0, self.fecundity())
            return int(fecundity * population_size)


        # Increase adjacent populations if they are too small.
        # Add population to unoccupied adjacent tiles.
        for adjacent_tile in tile.get_neighbors():
            if adjacent_tile.contains(self):
                # The tile is occupied by this species.
                adjacent_population_size = adjacent_tile.get_population(self)

                if adjacent_population_size < int(population_size * self.invasiveness()):
                    # The adjacent tile has a population that is too small.
                    new_pop = calculate_offspring()
                    tile.add_population(self, new_pop)
            else:
                # The adjacent tile is unoccupied
                new_pop = calculate_offspring()
                tile.add_population(self, new_pop)


    def get_footprint(self):
        # Estimate of the footprint area of an individual
        return math.log(self.height())**2
