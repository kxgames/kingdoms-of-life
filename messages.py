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
        self.price = self.city.get_price()

    def check(self, world, sender):
        city = self.city
        price = self.price
        player = city.player

        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "City requested by wrong player."
            return False

        # Make sure the player can afford this city.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d for a new city." % price
            return False

        # Make sure this city can be placed here.
        if not player.can_place_city(city):
            self.error = "Can't place a city in that location."
            return False

        return True

    def reject(self, actor):
        actor.reject_create_city(self)

    def setup(self, world, sender, id):
        self.city.give_id(id)

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
            self.error = "Road requested by wrong player."
            return False

        # Make sure the right player owns the cities being connected.
        if (player is not start.player) or (player is not end.player):
            self.error = "Can't build roads to enemy cities."
            return False

        # Make sure the player can afford this road.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d for a new road." % price
            return False

        # Make sure this road doesn't already exist.
        for other in player.roads:
            if road.has_same_route(other):
                self.error = "Can't make two roads between the same cities."
                return False

        # Make sure neither end of the road is under battle.
        if start.is_in_battle() or end.is_in_battle():
            self.error = "Can't build a road to a city under battle."
            return False

        # Make sure there are no obstacles in the way of this road.
        if not player.can_place_road(road):
            self.error = "Can't build a road through an existing city."
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


class CreateArmy (kxg.Message):

    def __init__(self, player, position):
        self.army = tokens.Army(player, position)
        self.price = tokens.Army.get_next_price(player)

    def check(self, world, sender):
        army = self.army
        price = self.price
        player = army.player

        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "Army requested by wrong player."
            return False

        # Make sure the player can afford this army.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d for a new army." % price
            return False

        # Make sure this army can be placed here.
        if not player.can_place_army(army):
            self.error = "Can't place an army in that location."
            return False

        return True

    def reject(self, actor):
        actor.reject_create_army(self)

    def setup(self, world, sender, id):
        self.army.give_id(id)

    def execute(self, world):
        world.create_army(self.army, self.price)

    def notify(self, actor, is_mine):
        actor.create_army(self.army, is_mine)



class UpgradeCity (kxg.Message):

    def __init__(self, city):
        self.city = city
        self.price = city.get_upgrade_price()

    def check(self, world, sender):
        city = self.city
        player = city.player
        price = self.price
        
        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "Upgrade requested by wrong player."
            return False

        # Make sure the city in question is actually under battle.
        if city.is_in_battle():
            self.error = "Can't upgrade a city that is under battle."
            return False

        # Make sure the player can afford this defense.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to upgrade this city." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_upgrade_city(self)

    def execute(self, world):
        world.upgrade_city(self.city, self.price)

    def notify(self, actor, is_mine):
        actor.upgrade_city(self.city, is_mine)


class UpgradeArmy (kxg.Message):

    def __init__(self, army):
        self.army = army
        self.price = army.get_upgrade_price()

    def check(self, world, sender):
        army = self.army
        player = army.player
        price = self.price
        
        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "Upgrade requested by wrong player."
            return False

        # Make sure the army in question is actually under battle.
        if army.is_in_battle():
            self.error = "Can't upgrade a army that is under attack."
            return False

        # Make sure the player can afford this defense.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to upgrade this army." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_upgrade_army(self)

    def execute(self, world):
        world.upgrade_army(self.army, self.price)

    def notify(self, actor, is_mine):
        actor.upgrade_army(self.army, is_mine)



class AttackCity (kxg.Message):

    def __init__(self, attacker, city):
        self.battle = tokens.Battle(attacker, city)
        self.price = city.get_attack_price(attacker)

    def check(self, world, sender):
        attacker = self.battle.attacker
        city = self.battle.city
        price = self.price

        # Make sure the right player is sending this message.
        if sender is not attacker:
            self.error = "Attack requested by wrong player."
            return False

        # Make sure the attacker has at least one city themselves.
        if not attacker.cities:
            self.error = "You must build a city before attacking your opponent."
            return False

        # Make sure this city is not already under battle.
        if city.is_in_battle():
            self.error = "Can't attack a city that is already under battle."
            return False

        # Make sure the player can afford this attack.
        if not attacker.can_afford_price(price):
            self.error = "Can't afford $%d to attack this city." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_attack_city(self)

    def setup(self, world, sender, id):
        self.battle.give_id(id)

    def execute(self, world):
        world.attack_city(self.battle, self.price)

    def notify(self, actor, was_me):
        actor.attack_city(self.battle, was_me)


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
            self.error = "Defense requested by wrong player."
            return False

        # Make sure the city in question is actually under battle.
        if not city.is_in_battle():
            self.error = "Can't defend a city that isn't under battle."
            return False

        # Make sure the player can afford this defense.
        if not defender.can_afford_price(price):
            self.error = "Can't afford $%d to defend this city." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_defend_city(self)

    def execute(self, world):
        world.defend_city(self.city.battle, self.price)

    def notify(self, actor, was_me):
        actor.defend_city(self.city, was_me)


class CaptureCity (kxg.Message):

    def __init__(self, battle):
        self.battle = battle

    def check(self, world, sender):
        return self.battle.was_successful()

    def execute(self, world):
        world.capture_city(self.battle)

    def notify(self, actor, sent_from_here):
        actor.capture_city(self.battle)


class DefeatPlayer (kxg.Message):

    def __init__(self, player):
        self.player = player

    def check(self, world, sender):
        return self.player.was_defeated()

    def execute(self, world):
        world.defeat_player(self.player)

    def notify(self, actor, sent_from_here):
        actor.defeat_player(self.player)



# undefined functions:
# city: get_upgrade_price()
# actor: reject_upgrade_city(self)
# world: upgrade_city(city, price)
# actor: upgrade_city(city, is_mine)
# 
# army: get_upgrade_price()
# actor: reject_upgrade_army(self)
# world: upgrade_army(army, price)
# actor: upgrade_army(army, is_mine)
# 
# Army: init(player, position)
# Army: get_next_price(player)
# player: can_place_army(army)
# actor: reject_create_army(self)
# army: give_id(id)
# world: create_army(army, price)
# actor: create_army(army, is_mine)


# Messages to create:
# Move army: <F-drag>, start on army.
# Attack army: <F-drag>, drag onto enemy army.
# Join Battle: <F-drag>, drag onto enemy city/army in existing battle.
# Retreat army: <F-drag>, drag out of existing battle.
# Destroy army: N/A



# Build city: <D-click>, within territory but not on existing city.
# Upgrade city: <D-click>, on existing city.
# Build road: <D-drag>, between cities.

# Build army: <F-click>, within territory.
# Upgrade army: <F-click>, on existing army.
# Move army: <F-drag>, start on army.
# Attack city: <F-drag>, drag onto enemy city.
# Attack army: <F-drag>, drag onto enemy army.
# Join Battle: <F-drag>, drag onto enemy city/army in existing battle.
# Retreat army: <F-drag>, drag out of existing battle.
# Destroy army: N/A

# Hotkey   Mnemonic
# ======   ========
# D        Develop
# F        Fight

# GUI
# ===
# 1. Show city/army HP?  Yes.
# 2. Show battles?  No.
# 3. Show battle request?  Dotted line between army and target.
# 3. Suck armies into battles? Must close to within some radius.
