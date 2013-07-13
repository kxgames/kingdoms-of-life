#!/usr/bin/env python

import argparse
import kxg, armedcat

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', default=53351, type=int)
parser.add_argument('--wealthy', '-w', action='store_true')
parser.add_argument('--batch', '-b', action='store_true')
arguments = parser.parse_args()
host, port = 'localhost', arguments.port

if arguments.wealthy:
    import tokens
    tokens.Player.starting_wealth = 10000

if arguments.batch:
    armedcat.use_gui = False
    armedcat.ClientLoop = armedcat.PygameClientLoop
else:
    armedcat.use_gui = True
    armedcat.ClientLoop = armedcat.PygletClientLoop

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", armedcat.ServerLoop(host, port))
debugger.loop("Alice", armedcat.ClientLoop("Alice", host, port))
debugger.loop("Bob", armedcat.ClientLoop("Bob", host, port))

debugger.run()
