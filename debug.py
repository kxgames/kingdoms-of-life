#!/usr/bin/env python

import argparse
import kxg, slimycat

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', default=53351, type=int)
arguments = parser.parse_args()
host, port = 'localhost', arguments.port

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", slimycat.ServerLoop(host, port))
debugger.loop("Client-1", slimycat.ClientLoop("Client 1", host, port))
debugger.loop("Client-2", slimycat.ClientLoop("Client 2", host, port))

debugger.run()
