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

    def execute(self, world):
        world.game_over(self.winner)

    def notify(self, actor, sent_from_here):
        actor.game_over(self.winner)



class CreatePlayer (kxg.Greeting):

    def __init__(self, name, color):
        self.player = tokens.Player(name, color)

    def get_sender(self):
        return self.player

    def check(self, world, sender):
        return not world.has_game_started()

    def setup(self, world, sender, id):
        self.player.give_id(id)

    def execute(self, world):
        world.create_player(self.player)

    def notify(self, actor, is_mine):
        actor.create_player(self.player, is_mine)


class CreateCity (kxg.Message):

    def __init__(self, player, position):
        self.city = tokens.City(player, position)
        self.price = tokens.City.get_next_price(player)

    def check(self, world, sender):
        city = self.city
        price = self.price
        player = city.player

        # Make sure the right player is sending this message.
        if sender is not player:
            print "City requested by wrong player."
            return False

        # Make sure the player can afford this city.
        if not player.can_afford_price(price):
            print "Can't afford $%d for a new city." % price
            return False

        # Make sure this city can be placed here.
        if not player.can_place_city(city):
            print "Can't place a city in that location."
            return False

        return True

    def reject(self, actor):
        actor.reject_create_city(self)

    def setup(self, world, sender, id):
        self.city.give_id(id)
        self.city.level = tokens.City.get_next_level()

    def execute(self, world):
        world.create_city(self.city, self.price)

    def notify(self, actor, is_mine):
        actor.create_city(self.city, is_mine)


class CreateRoad (kxg.Message):

    def __init__(self, player, start, end):
        self.road = tokens.Road(player, start, end)
        self.price = self.road.get_price()

    def check(self, world, sender):
        road = self.road; price = self.price
        player = road.player; start = road.start; end = road.end

        # Make sure the right player is sending this message.
        if sender is not player:
            print "Road requested by wrong player."
            return False

        # Make sure the right player owns the cities being connected.
        if (player is not start.player) or (player is not end.player):
            print "Can't build roads to enemy cities."
            return False

        # Make sure the player can afford this road.
        if not player.can_afford_price(price):
            print "Can't afford $%d for a new road." % price
            return False

        # Make sure this road doesn't already exist.
        for other in player.roads:
            if road.has_same_route(other):
                print "Can't make two roads between the same cities."
                return False

        # Make sure neither end of the road is under siege.
        if start.is_under_siege() or end.is_under_siege():
            print "Can't build a road to a city under siege."
            return False

        # Make sure this road doesn't cross through enemy territory.
        if not player.can_place_road(road):
            print "Can't place a road in enemy territory."
            return False

        return True

    def reject(self, actor):
        actor.reject_create_road(self)

    def setup(self, world, sender, id):
        self.road.give_id(id)

    def execute(self, world):
        world.create_road(self.road, self.price)

    def notify(self, actor, is_mine):
        actor.create_road(self.road, is_mine)



class AttackCity (kxg.Message):

    def __init__(self, attacker, city):
        self.siege = tokens.Siege(attacker, city)
        self.price = city.get_attack_price()

    def check(self, world, sender):
        attacker = self.siege.attacker
        city = self.siege.city
        price = self.price

        # Make sure the right player is sending this message.
        if sender is not attacker:
            print "Attack requested by wrong player."
            return False

        # Make sure this city is not already under siege.
        if city.is_under_siege():
            print "Can't attack a city that is already under siege."
            return False

        # Make sure the player can afford this attack.
        if not attacker.can_afford_price(price):
            print "Can't afford $%d to attack this city." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_attack_city(self)

    def setup(self, world, sender, id):
        self.siege.give_id(id)

    def execute(self, world):
        world.attack_city(self.siege, self.price)

    def notify(self, actor, was_me):
        actor.attack_city(self.siege, was_me)


class DefendCity (kxg.Message):

    def __init__(self, city):
        self.city = city
        self.price = city.get_defense_price()

    def check(self, world, sender):
        city = self.city
        defender = self.city.player
        price = self.price

        # Make sure the right player is sending this message.
        if sender is not defender:
            print "Defense requested by wrong player."
            return False

        # Make sure the city in question is actually under siege.
        if not city.is_under_siege():
            print "Can't defend a city that isn't under siege."
            return False

        # Make sure the player can afford this defense.
        if not defender.can_afford_price(price):
            print "Can't afford $%d to defend this city." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_defend_city(self)

    def execute(self, world):
        world.defend_city(self.city.siege, self.price)

    def notify(self, actor, was_me):
        actor.defend_city(self.city, was_me)


class CaptureCity (kxg.Message):

    def __init__(self, siege):
        self.siege = siege

    def check(self, world, sender):
        return self.siege.was_successful()

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

