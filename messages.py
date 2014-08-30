import kxg
import tokens

class Message (kxg.Message):

    def reject(self, actor):
        actor.show_error(self)


class WelcomeClient (object):

    def __init__(self, name):
        from string import capwords
        self.name = capwords(name)

    def __str__(self):
        return '<WelcomeClient>'


class StartGame (Message):

    def __str__(self):
        return '<StartGame>'

    def check(self, world, sender_id):
        return self.was_sent_by_referee(sender_id) \
                and not world.has_game_started()

    def setup(self, world, id):
        self.map = tokens.Map('maps/mediterranean.200x153.png')
        self.map.give_id(id)

    def execute(self, world):
        world.start_game(self.map)


class GameOver (Message):

    def __init__(self, winner):
        self.winner = winner

    def __str__(self):
        return '<GameOver>'

    def check(self, world, sender_id):
        return self.was_sent_by_referee(sender_id)

    def execute(self, world):
        world.game_over(self.winner)



class CreatePlayer (Message):

    def __init__(self, name, color):
        self.player = tokens.Player(name, color)
        self.city = None

    def __str__(self):
        return '<CreatePlayer>'

    def check(self, world, sender):
        self.player.set_actor(sender)
        return True

    def setup(self, world, id):
        import random
        self.player.give_id(id)

    def execute(self, world):
        world.create_player(self.player)


class CreateCity (Message):

    def __init__(self, player, position):
        self.city = tokens.City(player, position)
        self.price = player.get_city_price()

    def __str__(self):
        return '<CreateCity>'

    def check(self, world, sender):
        city = self.city
        player = city.player

        # Make sure the right player is sending this message.
        if sender.player is not player:
            self.error = "City requested by wrong player."
            return False

        # Make sure the player is still alive.
        if player.was_defeated():
            self.error = "Defeated players can't build cities."
            return False

        # Make sure the player can afford this city.
        if not player.can_afford_price(self.price):
            self.error = "Can't afford $%d for a new city." % self.price
            return False

        # Make sure this city can be placed here.
        if not player.can_place_city(city):
            self.error = "Can't place a city in that location."
            return False

        return True

    def setup(self, world, id):
        self.city.give_id(id)

    def execute(self, world):
        world.create_city(self.city, self.price)


class CreateArmy (Message):

    def __init__(self, player, position):
        self.army = tokens.Army(player, position)
        self.price = player.get_army_price()

    def __str__(self):
        return '<CreateArmy>'

    def check(self, world, sender):
        army = self.army; player = army.player
        self.price = player.get_army_price()

        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Army requested by wrong player."
            return False

        # Make sure the player is still alive.
        if player.was_defeated() or not player.is_registered():
            self.error = "Defeated players can't build armies."
            return False

        # Make sure the player can afford this army.
        if not player.can_afford_price(self.price):
            self.error = "Can't afford $%d for a new army." % self.price
            return False

        # Make sure this army can be placed here.
        if not player.can_place_army(army):
            self.error = "Can't place an army in that location."
            return False

        return True

    def setup(self, world, id):
        self.army.give_id(id)

    def execute(self, world):
        world.create_army(self.army, self.price)


class CreateRoad (Message):

    def __init__(self, player, start, end):
        self.road = tokens.Road(player, start, end)
        self.price = player.get_road_price()

    def __str__(self):
        return '<CreateRoad>'

    def check(self, world, sender):
        road = self.road; price = self.price
        player = road.player; start = road.start; end = road.end

        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Road requested by wrong player."
            return False

        # Make sure the player is still alive.
        if player.was_defeated():
            self.error = "Defeated players can't build roads."
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

    def setup(self, world, id):
        self.road.give_id(id)

    def execute(self, world):
        world.create_road(self.road, self.price)



class UpgradeCommunity (Message):

    def __init__(self, community):
        self.community = community

    def __str__(self):
        return '<UpgradeCommunity>'

    def check(self, world, sender):
        community = self.community
        player = community.player
        price = self.community.get_upgrade_price()
        
        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Upgrade requested by wrong player."
            return False

        # Make sure the player is still alive.
        if player.was_defeated():
            self.error = "Defeated players can't upgrade cities."
            return False

        # Make sure the community still exists.
        if community.is_after_teardown():
            self.error = "Community was already removed from the world."
            return False

        # Communities can't be upgraded beyond level 5.
        if community.get_level() >= community.get_maximum_level():
            title = "Cities" if community.is_city() else "Armies"
            self.error = "%s can't be upgraded beyond level 5." % title
            return False

        # Make sure the community in question is not in a battle.
        if community.is_in_battle():
            self.error = "Can't upgrade a community that's engaged in a battle."
            return False

        # Make sure the player can afford to upgrade the community.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to upgrade this community." % price
            return False

        return True

    def execute(self, world):
        world.upgrade_community(self.community, self.community.get_upgrade_price())


class MoveArmy (Message):

    def __init__(self, army, end_point):
        self.army = army
        self.target = end_point

    def __str__(self):
        return '<MoveArmy>'

    def check(self, world, sender):
        army = self.army
        target = self.target
        player = army.player

        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Army motion requested by wrong player."
            return False

        # Make sure the army still exists.
        if army.is_after_teardown():
            self.error = "Army was already removed from the world."
            return False

        # Make sure the player is still alive.
        if player.was_defeated():
            self.error = "Defeated players can't move armies."
            return False

        # Make sure the army is not already in a battle.
        if army.battle:
            self.error = "Army can't move when it is in a battle."
            return False

        # Make sure the army can move to the end point.
        if not army.can_move_to(target):
            self.error = "Army can't move there."
            return False

        return True

    def execute(self, world):
        self.army.move_to(self.target)


class DestroyArmy (Message):
    
    def __init__(self, army):
        self.army = army

    def __str__(self):
        return '<DestroyArmy>'

    def check(self, world, sender):
        army = self.army
        
        # Make sure this army still exists.
        if army.is_after_teardown():
            self.error = "Army was already removed from the world."
            return False

        # Make sure the army is actually an army.
        if not isinstance(army, tokens.Army):
            self.error = "Community must be an army."
            return False

        # Make sure the army is at 0 health.
        if not army.get_health() <= 0:
            self.error = "Army must be at zero health to be destroyed."
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.destroy_army(self.army)


class DefeatPlayer (Message):

    def __init__(self, player):
        self.player = player

    def __str__(self):
        return '<DefeatPlayer>'

    def check(self, world, sender):
        return self.player.was_defeated() and not self.player.is_dead()

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.defeat_player(self.player)


class RequestBattle (Message):

    def __init__(self, army, community):
        self.campaign = tokens.Campaign(army, community)

    def __str__(self):
        return '<RequestBattle>'

    def check(self, world, sender):
        army = self.campaign.army
        community = self.campaign.community
        player = army.player
        price = army.get_battle_price()

        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Battle requested by wrong player."
            return False

        # Make sure the player is still alive.
        if player.was_defeated():
            self.error = "Defeated players can't request battles."
            return False

        # Make sure this army still exists.
        if army.is_after_teardown():
            self.error = "Army was already removed from the world."
            return False

        # Make sure the target community still exists.
        if community.is_after_teardown():
            self.error = "Target was already removed from the world."
            return False

        # Make sure the army is not attacking one of its own.
        if community.player is player:
            self.error = "Army can't attack friendly community."
            return False
        
        # Make sure the army is not already in a battle.
        if army.battle:
            self.error = "Army can't start a new battle while it is already in one."
            return False

        # Make sure the army is not chasing anyone.
        if army.is_chasing():
            self.error = "Army can't start a new campaign while it is already on one."
            return False

        # Make sure the army can move to the end point.
        if not army.can_request_battle(community):
            self.error = "Army can't move there."
            return False
        
        # Only charge the player for starting a battle.
        if not community.is_in_battle():
            # Make sure the player can afford to battle community.
            if not player.can_afford_price(price):
                self.error = "Can't afford $%d to battle this community." % price
                return False

        return True

    def setup (self, world, id):
        self.campaign.give_id(id)

    def execute(self, world):
        world.request_battle(self.campaign)


class StartBattle (Message):

    def __init__(self, campaign):
        self.campaign = campaign
        self.battle = tokens.Battle(campaign)

    def __str__(self):
        return '<StartBattle>'

    def check(self, world, sender):
        army = self.campaign.army
        target = self.campaign.community

        # Make sure the campaign still exists.
        if self.campaign.is_after_teardown():
            self.error = "Campaign was already removed from the world."
            return False
        
        # Make sure the army is not attacking one of its own.
        if target.player is army.player:
            self.error = "Army can't attack friendly targets."
            return False
        
        # Make sure the army is not already in a battle.
        if army.battle:
            self.error = "Army can't start a new battle while it is already in one."
            return False
        
        # Make sure the target is not already in a battle.
        # Use JoinBattle if they are.
        if target.battle:
            self.error = "Army can't start a new battle with the target."
            return False

        # Check proximity to the target.
        if not army.check_engagement_proximity(target):
            self.error = "Army must be close to the target to start battle."
            return False

        return True

    def setup(self, world, id):
        self.battle.give_id(id)

    def execute(self, world):
        world.start_battle(self.campaign, self.battle)


class JoinBattle (Message):

    def __init__(self, campaign, battle):
        self.campaign = campaign
        self.battle = battle

    def __str__(self):
        return '<JoinBattle>'

    def check(self, world, sender):
        army = self.campaign.army
        community = self.campaign.community
        
        # Make sure the campaign still exists.
        if self.campaign.is_after_teardown():
            self.error = "Campaign was already removed from the world."
            return False
        
        # Make sure the battle still exists.
        if self.battle.is_after_teardown():
            self.error = "Battle was already removed from the world."
            return False
        
        # If the community is friendly, then the army is coming to it's aid.  
        # No need to check ownership.
        
        # Make sure the army is not already in a battle.
        if army.battle:
            self.error = "Army can't start a new battle while it is already in one."
            return False
        
        # Make sure the target is in a battle.  Use StartBattle if it isn't.
        if not community.battle:
            self.error = "Target must be in a battle for the army to join."
            return False

        # Check proximity to the battle.
        if not army.check_battle_proximity(community.battle):
            self.error = "Army must be close to an enemy target to join a battle."
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.join_battle(self.campaign, self.battle)



class RetreatBattle (Message):
    
    def __init__(self, army):
        self.army = army
        self.battle = army.battle

    def __str__(self):
        return '<RetreatBattle>'

    def check(self, world, sender):
        army = self.army
        player = army.player
        self.price = army.get_retreat_price()
        
        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Retreat requested by wrong player."
            return False

        # Make sure the army is actually an army.
        if not isinstance(army, tokens.Army):
            self.error = "Only armies can retreat."
            return False

        # Make sure the army still exists.
        if self.army.is_after_teardown():
            self.error = "Army was already removed from the world."
            return False

        # Make sure the army is in a battle or campaign.
        if not army.battle and not army.my_campaign:
            self.error = "Army must be in a battle or campaign to retreat."
            return False

        # Make sure the battle still exists.
        if army.battle and self.army.battle.is_after_teardown():
            self.error = "Battle was already removed from the world."
            return False

        # Make sure the campaign still exists.
        if army.my_campaign and self.army.my_campaign.is_after_teardown():
            self.error = "Campaign was already removed from the world."
            return False

        # Make sure the player can afford to retreat.
        if not player.can_afford_price(self.price):
            self.error = "Can't afford $%d to retreat from battle." % self.price
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.retreat_battle(self.army, self.price)


class ReinforceCommunity (Message):

    def __init__(self, community):
        self.community = community

    def __str__(self):
        return '<ReinforceArmy>'

    def check(self, world, sender):
        community = self.community
        player = community.player
        price = community.get_reinforce_price()
        name = 'army' if community.is_army() else 'city'
        
        # Make sure the right player is sending this message.
        if sender is not player.actor:
            self.error = "Reinforcements requested by wrong player."
            return False

        # Make sure the community still exists.
        if community.is_after_teardown():
            self.error = "%s was already removed from the world." % name.title()
            return False

        # Make sure the army is in a battle or campaign.
        if not community.is_in_battle():
            self.error = "%s must be in a battle to be reinforced." % name.title()
            return False

        # Make sure the battle still exists.
        if community.is_in_battle() and community.battle.is_after_teardown():
            self.error = "Battle was already removed from the world."
            return False

        # Make sure the player can afford to retreat.
        if not player.can_afford_price(price):
            self.error = "Can't afford $%d to reinforce this %s." % (price, name)
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.reinforce_community(self.community)


class ZombifyCity (Message):
    
    def __init__(self, city):
        self.city = city
        self.battle = city.battle

    def __str__(self):
        return '<ZombifyCity>'

    def check(self, world, sender):
        city = self.city
        
        # Make sure the city still exists.
        if city.is_after_teardown():
            self.error = "City was already removed from the world."
            return False

        # Make sure the city is actually an city.
        if not isinstance(city, tokens.City):
            self.error = "Only cities can be zombified."
            return False

        # Make sure the city is in a battle.
        if not city.battle:
            self.error = "City must be in a battle to be zombified."
            return False
        
        # Make sure the city is at 0 health.
        if not city.get_health() <= 0:
            self.error = "City must be at zero health to be zombified."
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.zombify_city(self.city.battle, self.city)


class EndBattle (Message):
    
    def __init__(self, battle):
        self.battle = battle

    def __str__(self):
        return '<EndBattle>'

    def check(self, world, sender):
        
        # Make sure the battle still exists.
        if self.battle.is_after_teardown():
            self.error = "Battle was already removed from the world."
            return False

        # Make sure the battle is actually over.
        if not self.battle.was_successful():
            self.error = "Can't end the battle, battle is still in progress."
            return False

        return True

    def setup(self, world, id):
        pass

    def execute(self, world):
        world.end_battle(self.battle)



