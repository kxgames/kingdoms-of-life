import kxg
import tokens
import random

class WelcomeClient (object):
    def __init__(self, name):
        from string import capwords
        self.name = capwords(name)

class StartGame (kxg.Message):

    def __init__(self):
        self.map = None

    def check(self, world, sender):
        return not world.has_game_started()

    def setup(self, world, sender, id):
        self.map = tokens.Map(id)
        self.request = tokens.TradeRequest(id, "Kale", "Grain")

    def execute(self, world):
        world.start_game()
        world.create_map(self.map, self.request)

    def notify(self, actor, sent_from_here):
        actor.start_game()


class GameOver (kxg.Message):

    def __init__(self, winner):
        self.winner = winner

    def check(self, world, sender):
        return sender == 'referee'

    def execute(self, status):
        pass

    def notify(self, actor, sent_from_here):
        pass



class CreatePlayer (kxg.Greeting):

    def __init__(self, name, color):
        self.player = tokens.Player(name, color)

    def get_sender(self):
        return self.player

    def check(self, world, sender):
        return not world.has_game_started()

    def setup(self, world, sender, id):
        self.player.register(id)

    def execute(self, world):
        world.create_player(self.player)

    def notify(self, actor, is_mine):
        actor.create_player(self.player, is_mine)


class CreateCity (kxg.Message):

    def __init__(self, player, position):
        self.player = player
        self.city = tokens.City(position)

    def check(self, world, sender):
        player = self.player
        road = self.road

        # Make sure the right player is sending this message.
        if sender is not player:
            return False

        # Make sure the player can afford this city.
        if not player.can_afford_city(city):
            return False

        # Make sure this city can be placed here.
        if not player.can_place_city(city):
            return False

        return True

    def reject(self, actor):
        actor.reject_create_city(self.city)

    def setup(self, world, sender, id):
        self.city.register(id)
        self.city.level = tokens.City.next_level()

    def execute(self, world):
        world.place_city(self.player, self.city)

    def notify(self, actor, is_mine):
        actor.place_city(self.city, is_mine)


class CreateRoad (kxg.Message):

    def __init__(self, player, start, end):
        self.player = player
        self.road = tokens.Road(start, end)

    def check(self, world, sender):
        player = self.player
        road = self.road

        # Make sure the right player is sending this message.
        if sender is not player:
            return False

        # Make sure the player can afford this road.
        if not player.can_afford_road(road, world):
            return False

        # Make sure this road doesn't cross through enemy territory.
        if not player.can_place_road(road, world):
            return False

        return True

    def reject(self, actor):
        actor.reject_create_road(self.road)

    def setup(self, world, sender, id):
        self.road.register(id)

    def execute(self, world):
        world.create_road(self.player, self.road)

    def notify(self, actor, is_mine):
        actor.create_road(self.road, is_mine)



class EnactSiege:
    pass

class LiftSiege:
    pass

