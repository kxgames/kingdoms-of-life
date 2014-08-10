#!/usr/bin/env python3

import seacow
import arguments

arguments.parser.add_argument('--host', '-x', default='kxgames.net')
arguments.parser.add_argument('--port', '-p', default=53351, type=int)
arguments.parse_args()

game = seacow.ServerLoop(arguments.host, arguments.port)
game.play()

