import traits

class Tile:
    def __init__(self, side_length):
        
        self.length = side_length
        self.area = side_length**2

        self.plants{} # { family : population }
        self.animals{} # { family : population }

        # Tile traits
        self.temperature = traits.GaussTrait()
        self.humidity = traits.GaussTrait()
        self.fertility = traits.ValueTrait()
        self.insolation = traits.ValueTrait()
        self.fire = traits.ValueTrait()

    def get_plant_population(self, plant):
        return self.plants[plant]

    def get_population(self, family):
        for families in self.plants, self.animals:
            try:
                return families[family]
            except KeyError:
                continue
        raise KeyError

    def add_plant_population(self, plant, new_population):
        try:
            self.plants[plant] += new_population
        except KeyError:
            self.plants[plant] = new_population

    # Example trait getter function
    def get_insolation(self, height=0):
        # Calculate effective insolation.
        # Accounts for shade of taller plants
        max_height = height
        ratio = 1
        for plant in self.plants:
            # Some function....
            # This one should return the portion of sunlight that 
            # reaches the desired height based on the tallest plant on 
            # the tile.
            # Future? Sum up effects of all taller plants
            if plant.height > max_height:
                max_height = plant.height
                footprint = plant.get_footprint()
                population_footprint = footprint * self.get_population(plant)

                ratio = 1.0 - population_footprint / self.area
                if ratio < 0.1:
                    ratio = 0.1
                    break

        return self.insolation * ratio

    def get_raw_insolation(self):
        # Return the raw insolation value.
        return self.insolation

        
