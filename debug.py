#!/usr/bin/env python3

import kxg
import seacow
import arguments

arguments.parser.add_argument('--port', '-p', default=53351, type=int)
arguments.parse_args()
host, port = 'localhost', arguments.port

debugger = kxg.MultiplayerDebugger()

debugger.loop("Server", seacow.ServerLoop(host, port))
debugger.loop("Alice", seacow.ClientLoop("Alice", host, port))
debugger.loop("Bob", seacow.ClientLoop("Bob", host, port))

debugger.run()
