#!/usr/bin/env python

# Imports (fold)
from __future__ import division

import kxg
import gui, messages

from kxg.geometry import Vector
from functools import partial


def update_for_alice(self, time):
    message = None
    self.frame += 1

    if self.frame == 25:
        position = Vector(250.00, 250.00)
        message = messages.CreateCity(self.player, position)

    #if self.frame == 25:
    #    position = Vector(216.00, 318.00)
    #    message = messages.CreateCity(self.player, position)

    #if self.frame == 240:
    #    position = Vector(238.00, 317.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 309:
    #    position = Vector(260.00, 311.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 344:
    #    position = Vector(307.00, 279.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 367:
    #    position = Vector(358.00, 248.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 390:
    #    position = Vector(408.00, 210.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 414:
    #    position = Vector(457.00, 173.00)
    #    message = messages.CreateArmy(self.player, position)

    if message is not None:
        self.send_message(message)

def update_for_bob(self, time):
    message = None
    self.frame += 1

    if self.frame == 50:
        position = Vector(250.00, 300.00)
        message = messages.CreateArmy(self.player, position)

    if self.frame == 75:
        selection = self.world.get_token(5)
        target = self.world.get_token(4)
        message = messages.RequestBattle(selection, target)

    #if self.frame == 562:
    #    position = Vector(213.00, 308.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 598:
    #    position = Vector(225.00, 257.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 626:
    #    position = Vector(249.00, 206.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 660:
    #    position = Vector(296.00, 157.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 684:
    #    position = Vector(328.00, 123.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 709:
    #    position = Vector(368.00, 101.00)
    #    message = messages.CreateArmy(self.player, position)

    #if self.frame == 783:
    #    selection = self.world.get_token(11)
    #    target = self.world.get_token(4)
    #    message = messages.RequestBattle(selection, target)

    if message is not None:
        self.send_message(message)


class ReplayActor (kxg.Actor):

    def __init__(self, name):
        kxg.Actor.__init__(self)
        self.frame = 0

        if name == 'Alice':
            self.update = partial(update_for_alice, self)
        if name == 'Bob':
            self.update = partial(update_for_bob, self)

    def get_name(self):
        return "replay"

    def start_game(self):
        pass

    def game_over(self, winner):
        pass

    def create_player(self, player, is_mine):
        if is_mine: self.player = player

    def create_city(self, city, is_mine):
        pass

    def create_army(self, army, is_mine):
        pass

    def create_road(self, road, is_mine):
        pass

    def upgrade_community(self, community, is_mine):
        pass

    def destroy_army(self, army, is_mine):
        pass

    def request_battle(self, campaign, is_mine):
        pass

    def start_battle(self, battle):
        pass

    def join_battle(self, battle):
        pass

    def retreat_battle(self, army, target, is_mine):
        pass

    def zombify_city(self, battle, city, is_mine):
        pass

    def end_battle(self, battle, is_mine):
        pass

    def move_army(self, army, target, is_mine):
        pass

    def attack_city(self, battle, is_mine):
        pass

    def defend_city(self, battle, is_mine):
        pass

    def defeat_player(self):
        pass

    
    def show_error(self, message):
        print message.error


class GuiReplayActor (gui.Gui):

    def __init__(self, name, window):
        gui.Gui.__init__(self, window)
        self.frame = 0

        if name == 'Alice':
            self.update = partial(update_for_alice, self)
        if name == 'Bob':
            self.update = partial(update_for_bob, self)


    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass


