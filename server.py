#!/usr/bin/env python

import armedcat
import arguments

arguments.parser.add_argument('--host', '-x', default='kxgames.net')
arguments.parser.add_argument('--port', '-p', default=53351, type=int)
arguments.parse_args()

game = armedcat.ServerLoop(arguments.host, arguments.port)
game.play()

