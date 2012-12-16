#!/usr/bin/env python

import argparse
import slimycat

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--host', '-x', default='localhost')
parser.add_argument('--port', '-p', default=53351, type=int)

arguments = parser.parse_args()
name, host, port = arguments.name, arguments.host, arguments.port

game = slimycat.ClientLoop(name, host, port)
game.play()
