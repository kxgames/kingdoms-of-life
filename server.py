#!/usr/bin/env python

import argparse
import slimycat

parser = argparse.ArgumentParser()
parser.add_argument('--host', '-x', default='localhost')
parser.add_argument('--port', '-p', default=53351, type=int)

arguments = parser.parse_args()
host, port = arguments.host, arguments.port

game = slimycat.ServerLoop(host, port)
game.play()

