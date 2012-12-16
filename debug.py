#!/usr/bin/env python

import argparse
import kxg, slimycat

parser = argparse.ArgumentParser()
parser.add_argument('first_name')
parser.add_argument('second_name')
parser.add_argument('--port', '-p', default=53351, type=int)

arguments = parser.parse_args()
names = arguments.first_name.title(), arguments.second_name.title()
host, port = 'localhost', arguments.port

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", slimycat.ServerLoop(host, port))
debugger.loop("Client-" + names[0], slimycat.ClientLoop(names[0], host, port))
debugger.loop("Client-" + names[1], slimycat.ClientLoop(names[1], host, port))

debugger.run()
