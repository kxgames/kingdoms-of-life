import kxg
import tokens
import random

class WelcomeClient (object):
    def __init__(self, name):
        from string import capwords
        self.name = capwords(name)

class StartGame (kxg.Message):

    def check(self, world, sender):
        return not world.has_game_started()

    def execute(self, world):
        world.start_game()

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
        self.city = tokens.City(player, position)

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
        if not player.can_place_city(city, world):
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
        self.road = tokens.Road(player, start, end)

    def check(self, world, sender):
        player = self.player
        road = self.road

        # Make sure the right player is sending this message.
        if sender is not player:
            return False

        # Make sure the player can afford this road.
        if not player.can_afford_road(road):
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



class EnactSiege (kxg.Message):

    def __init__(self, attacker, city):
        self.siege = tokens.Siege(attacker, city)

    def check(self, world, sender):
        attacker = self.attacker
        siege = self.siege

        # Make sure the right attacker is sending this message.
        if sender is not attacker:
            return False

        # Make sure the attacker can afford this siege.
        if not attacker.can_afford_siege(siege):
            return False

        return True

    def reject(self, actor):
        actor.reject_enact_siege(self.siege)

    def setup(self, world, sender, id):
        self.siege.register(id)

    def execute(self, world):
        world.enact_siege(self.attacker, self.siege)

    def notify(self, actor, is_mine):
        actor.enact_siege(self.siege, is_mine)


class RelieveSiege (kxg.Message):

    def __init__(self, siege):
        self.siege = siege

    def check(self, world, sender):
        siege = self.siege
        defender = self.siege.city.player

        # Make sure the right attacker is sending this message.
        if sender is not defender:
            return False

        # Make sure the attacker can afford this siege.
        if not defender.can_afford_relief(siege):
            return False

        return True

    def reject(self, actor):
        actor.reject_enact_siege(self.siege)

    def setup(self, world, sender, id):
        self.siege.register(id)

    def execute(self, world):
        world.lift_siege(self.attacker, self.siege)

    def notify(self, actor, is_mine):
        actor.lift_siege(self.siege, is_mine)


class CaptureCity (kxg.Message):

    def __init__(self, siege):
        self.siege = siege

    def check(self, world, sender):
        return siege.was_successful()

    def execute(self, world):
        world.capture_city(self.siege)

    def notify(self, actor, sent_from_here):
        actor.capture_city(self.siege)


class DefeatPlayer (kxg.Message):

    def __init__(self, player):
        self.player = player

    def check(self, world, sender):
        return self.player.was_defeated()

    def execute(self, world):
        world.defeat_player(self.player)

    def notify(self, actor, sent_from_here):
        actor.defeat_player(self.player)

