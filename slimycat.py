#!/usr/bin/env python

import os, kxg
import tokens, gui, messages

class SandboxLoop (kxg.MainLoop):

    def __init__(self):
        world, referee = tokens.World(), tokens.Referee()
        actors_to_greetings = {
                gui.Gui(): messages.CreatePlayer("Sandbox", 'orange')}

        self.stage = kxg.SinglePlayerGameStage(
                world, referee, actors_to_greetings)
        
    def get_initial_stage(self):
        return self.stage


class ClientLoop (kxg.MainLoop):

    def __init__(self, name, nation, host, port):
        self.stage = ClientConnectionStage(name, nation, host, port)

    def get_initial_stage(self):
        return self.stage


class ServerLoop (kxg.MainLoop):

    def __init__(self, host, port):
        self.stage = ServerConnectionStage(host, port)

    def get_initial_stage(self):
        return self.stage



class ClientConnectionStage (kxg.Stage):

    def __init__(self, name, host, port):
        kxg.Stage.__init__(self)

        self.name = name
        self.update = self.update_connection
        self.client = kxg.network.PickleClient(
                host, port, callback=self.connection_established)

        self.pipe = None
        self.conversation = None
        self.successor = None

    def setup(self):
        pass

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
        world, actor, pipe = tokens.World(), gui.Gui(), self.pipe
        self.successor = kxg.MultiplayerClientGameStage(world, actor, pipe)

    def get_successor(self):
        return self.successor


class ServerConnectionStage (kxg.Stage):

    def __init__(self, host, port):
        kxg.Stage.__init__(self)

        self.pipes = []
        self.greetings = []
        self.colors = 'orange', 'purple'
        self.successor = None

        self.server = kxg.network.PickleServer(
                host, port, 2, self.clients_connected)

    def setup(self):
        print "SlimyCat server running. PID: %d" % os.getpid()
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
        print "Clients connected.  Game starting."
        world, referee = tokens.World(), tokens.Referee()
        pipes_to_messages = {}

        for greeting, color in zip(self.greetings, self.colors):
            pipe = greeting.get_pipe()
            name = greeting.get_message().name
            pipes_to_messages[pipe] = messages.CreatePlayer(name, color)

        self.successor = kxg.MultiplayerServerGameStage(
                world, referee, pipes_to_messages)

    def get_successor(self):
        return self.successor


