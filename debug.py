#!/usr/bin/env python

import kxg
import armedcat
import arguments

arguments.parser.add_argument('--port', '-p', default=53351, type=int)
arguments.parse_args()
host, port = 'localhost', arguments.port

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", armedcat.ServerLoop(host, port))
debugger.loop("Alice", armedcat.ClientLoop("Alice", host, port))
debugger.loop("Bob", armedcat.ClientLoop("Bob", host, port))

debugger.run()
