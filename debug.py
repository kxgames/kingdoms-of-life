#!/usr/bin/env python

import argparse
import kxg, armedcat

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', default=53351, type=int)
arguments = parser.parse_args()
host, port = 'localhost', arguments.port

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", armedcat.ServerLoop(host, port))
debugger.loop("Client-1", armedcat.ClientLoop("Client 1", host, port))
debugger.loop("Client-2", armedcat.ClientLoop("Client 2", host, port))
#debugger.loop("Client-3", armedcat.ClientLoop("Client 3", host, port))

debugger.run()
