#!/usr/bin/env python

import os, kxg, pyglet
import tokens, gui, messages

class SandboxLoop (kxg.Loop):

    def __init__(self):
        world = tokens.World()
        referee = tokens.Referee()
        window = pyglet.window.Window()
        actor = gui.Gui(window)

        actor.setup_pregame()

        actors_to_greetings = {
                actor: messages.CreatePlayer("Sandbox", 'orange')}

        game_stage = kxg.SinglePlayerGameStage(
                world, referee, actors_to_greetings)

        game_stage.successor = PostgameSplashStage(world, actor)

        kxg.Loop.__init__(self, game_stage)


class ServerLoop (kxg.Loop):

    def __init__(self, host, port):
        stage = ServerConnectionStage(host, port)
        kxg.Loop.__init__(self, stage)


class ClientLoop (kxg.GuiLoop):

    def __init__(self, name, host, port):
        stage = ClientConnectionStage(name, host, port)
        kxg.GuiLoop.__init__(self, stage)



class ServerConnectionStage (kxg.Stage):

    def __init__(self, host, port):
        kxg.Stage.__init__(self)

        self.pipes = []
        self.greetings = []
        self.successor = None
        self.host, self.port = host, port
        self.colors = 'orange', 'purple', 'green'

        self.server = kxg.network.Server(
                host, port, 2, self.clients_connected)

    def setup(self):
        print("Seacow server running: {}:{}".format(self.host, self.port))
        self.server.open()

    def update(self, time):
        if not self.server.finished():
            self.server.accept()
        else:
            pending_greetings = False
            for greeting in self.greetings:
                finished = greeting.update()
                if not finished: pending_greetings = True

            if not pending_greetings:
                self.exit_stage()

    def clients_connected(self, pipes):
        for pipe in pipes:
            greeting = kxg.messaging.SimpleReceive(
                    pipe, messages.WelcomeClient)
            greeting.start()

            self.pipes.append(pipe)
            self.greetings.append(greeting)

    def teardown(self):
        print("Clients connected.  Game starting.")
        world, referee = tokens.World(), tokens.Referee()
        pipes_to_messages = {}

        for greeting, color in zip(self.greetings, self.colors):
            pipe = greeting.get_pipe()
            name = greeting.get_message().name
            pipes_to_messages[pipe] = messages.CreatePlayer(name, color)

        self.successor = kxg.MultiplayerServerGameStage(
                world, referee, pipes_to_messages)

        self.successor.successor = ServerConnectionStage(
                self.host, self.port + 1)


    def get_successor(self):
        return self.successor


class ClientConnectionStage (kxg.Stage):

    def __init__(self, name, host, port):
        kxg.Stage.__init__(self)

        self.name = name
        self.host = host
        self.port = port

        self.update = self.update_connection
        self.client = kxg.network.Client(
                host, port, callback=self.connection_established)

        self.pipe = None
        self.conversation = None
        self.successor = None

    def setup(self):
        print("Seacow client running: {}:{} ({})".format(
            self.host, self.port, self.name))

        window = self.get_master().get_window()
        self.gui = gui.Gui(window)
        self.gui.setup_pregame()

    def update_connection(self, time):
        self.client.connect()

    def connection_established(self, pipe):
        message = messages.WelcomeClient(self.name)
        self.conversation = kxg.messaging.SimpleSend(pipe, message)
        self.conversation.start()

        self.pipe = pipe
        self.update = self.update_introduction

    def update_introduction(self, time):
        self.conversation.update()
        if self.conversation.finished():
            self.exit_stage()

    def teardown(self):
        world = tokens.World()
        actor = self.gui
        pipe = self.pipe

        game_stage = kxg.MultiplayerClientGameStage(world, actor, pipe)
        postgame_stage = PostgameSplashStage(
                world, actor, self.name, self.host, self.port)

        self.successor = game_stage
        game_stage.successor = postgame_stage

    def get_successor(self):
        return self.successor



class PostgameSplashStage (kxg.Stage):

    def __init__(self, world, gui, name='', host='', port=0):
        kxg.Stage.__init__(self)

        self.world = world
        self.gui = gui

        self.name = name
        self.host = host
        self.port = port

    def setup(self):
        with self.gui.lock():
            self.gui.setup_postgame()

    def update(self, time):
        pass

    def teardown(self):
        if self.gui.play_again:
            self.gui.teardown_postgame()
            self.successor = ClientConnectionStage(
                    self.name, self.host, self.port + 1)
            self.exit_stage()
        else:
            self.successor = None

    def is_finished(self):
        return self.gui.postgame_finished()

    def get_successor(self):
        return self.successor

