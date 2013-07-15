#!/usr/bin/env python

import argparse
import armedcat

parser = argparse.ArgumentParser()
parser.add_argument('--host', '-x', default='kxgames.net')
parser.add_argument('--port', '-p', default=53351, type=int)

arguments = parser.parse_args()
host, port = arguments.host, arguments.port

game = armedcat.ClientLoop('Client', host, port)
game.play()
