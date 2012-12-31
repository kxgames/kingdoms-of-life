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

        # Make sure neither end of the road is under siege.
        if start.is_under_siege() or end.is_under_siege():
            self.error = "Can't build a road to a city under siege."
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

        # Make sure the city in question is not under attack
        if city.is_under_siege():
            self.error = "Can't upgrade a city that is under siege."
            return False

        # Make sure the player can afford to upgrade the city.
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

        # Make sure the army in question is not under attack.
        if army.is_under_siege():
            self.error = "Can't upgrade a army that is under attack."
            return False

        # Make sure the player can afford to upgrade army.
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



class RequestBattle (kxg.Message):

    def __init__(self, army, target):
        self.army = army
        self.target = target
        self.price = target.get_battle_price()

    def check(self, world, sender):
        army = self.army
        target = self.target
        player = army.player
        price = self.price

        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "Battle requested by wrong player."
            return False

        # Make sure the army is not attacking one of its own.
        if target.player is player:
            self.error = "Army can't attack friendly targets."
            return False
        
        # Make sure the army is not already in a battle.
        if army.is_battling:
            self.error = "Army can't start a new battle while it is already in one."
            return False

        # Make sure the army can move to the end point.
        #if not army.can_move_to_target(army, target):
        #    self.error = "Army can't move there."
        #    return False
        
        # Make sure the player can afford to battle target.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to battle this target." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_request_battle(self)

    def execute(self, world):
        world.request_battle(self.army, self.target)

    def notify(self, actor, is_mine):
        actor.request_battle(self.army, self.target, is_mine)


class StartBattle (kxg.Message):

    def __init__(self, army, target):
        self.army = army
        self.target = self.target
        self.battle = None

    def check(self, world, sender):
        army = self.army
        target = self.target
        
        # Make sure the army is not attacking one of its own.
        if target.player is army.player:
            self.error = "Army can't attack friendly targets."
            return False
        
        # Make sure the army is not already in a battle.
        if army.is_battling:
            self.error = "Army can't start a new battle while it is already in one."
            return False
        
        # Make sure the target is not already in a battle.
        # Use JoinBattle if they are.
        if target.is_battling:
            self.error = "Army can't start a new battle with the target."
            return False

        # Check proximity to the target.
        if army.check_battle_proximity(army, target):
            self.error = "Army must be close to the target to start battle."
            return False

        return True

    def reject(self, actor):
        actor.reject_start_battle(self)

    def setup(self, world, sender, id):
        self.battle = tokens.Battle(army, target)
        self.battle.give_id(id)

    def execute(self, world):
        world.start_battle(self.battle)

    def notify(self, actor, sent_from_here):
        actor.start_battle(self.battle)


class JoinBattle (kxg.Message):

    def __init__(self, army, target):
        self.army = army
        self.target = self.target
        self.battle = None

    def check(self, world, sender):
        army = self.army
        target = self.target
        
        # If the target is friendly, then the army is coming to it's aid. 
        # No need to check ownership.
        
        # Make sure the army is not already in a battle.
        if army.is_battling:
            self.error = "Army can't start a new battle while it is already in one."
            return False
        
        # Make sure the target is in a battle.
        # Use StartBattle if they aren't.
        if target.is_battling:
            self.error = "Target must be in a battle for the army to join."
            return False

        # Check proximity to the target.
        if army.check_battle_proximity(army, target):
            self.error = "Army must be close to the target to join battle."
            return False

        return True

    def reject(self, actor):
        actor.reject_join_battle(self)

    def setup(self, world, sender, id):
        self.battle = self.target.battle
        self.battle.add_army(self.army)

    def execute(self, world):
        world.join_battle(self.battle)

    def notify(self, actor, sent_from_here):
        actor.join_battle(self.battle)


class RetreatBattle (kxg.Message):
    
    def __init__(self, army):
        self.army = army

    def check(self, world, sender):
        army = self.army
        
        # Make sure the army is in a battle.
        if not army.battle:
            self.error = "Army is not in a battle."
            return False

        self.price = army.battle.get_retreat_battle_price()
        
        # Make sure the player can afford to retreat.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to retreat from battle." % price
            return False

        return True

    def reject(self, actor):
        actor.reject_retreat_battle(self)

    def setup(self, world, sender, id):
        battle = self.army.battle
        battle.remove(army)

    def execute(self, world):
        world.retreat_battle(self.army, self.battle)

    def notify(self, actor, sent_from_here):
        actor.retreat_battle(self.battle)




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



class MoveArmy (kxg.Message):

    def __init__(self, army, end_point):
        self.army = army
        self.end = end_point

    def check(self, world, sender):
        army = self.army
        end = self.end
        player = army.player

        # Make sure the right player is sending this message.
        if sender is not player:
            self.error = "Army motion requested by wrong player."
            return False

        # Make sure the army can move to the end point.
        #if not army.can_move_to_position(army, end):
        #    self.error = "Army can't move there."
        #    return False

        return True

    def reject(self, actor):
        actor.reject_move_army(self)

    def execute(self, world):
        world.move_army(self.army, self.end)

    def notify(self, actor, is_mine):
        actor.move_army(self.army, self.end, is_mine)



## undefined helper functions:
#
## RetreatBattle
# army: get_retreat_battle_price()
# actor: reject_retreat_battle(self)
# world: retreat_battle(battle)
# actor: retreat_battle(battle)
#
## JoinBattle
# battle: add_army(army)
# world: join_battle(battle)
# actor: join_battle(battle)
#
## StartBattle
# - city: get_attack_price(attacker)
# - actor: reject_attack_city(self)
# - world: attack_city(battle, price)
# - actor: attack_city(battle, was_me)
# target: is_battling
# army: check_battle_proximity(army, target)
# tokens: Battle(army, target) ## instead of Battle(attacker, city)
# actor: reject_start_battle(self)
# world: start_battle(battle)
# actor: start_battle(battle)
#
## RequestBattle
# target: get_battle_price()
# army: can_move_to_target(army, target)
# actor: reject_request_battle(self)
# world: request_battle(army, target)
# actor: request_battle(army, target, is_mine)
#
## MoveArmy
# army: can_move_to_position(army, end)
# actor: reject_move_army(self)
# world: move_army(army, end)
# actor: move_army(army, end, is_mine)
# 
## CreateArmy
# Army: init(player, position)
# Army: get_next_price(player)
# player: can_place_army(army)
# actor: reject_create_army(self)
# army: give_id(id)
# world: create_army(army, price)
# actor: create_army(army, is_mine)
# 
## UpgradeArmy
# army: get_upgrade_price()
# actor: reject_upgrade_army(self)
# world: upgrade_army(army, price)
# actor: upgrade_army(army, is_mine)
#
## UpgradeCity
# city: get_upgrade_price()
# actor: reject_upgrade_city(self)
# world: upgrade_city(city, price)
# actor: upgrade_city(city, is_mine)




# Messages to create:
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
