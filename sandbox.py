#!/usr/bin/env python

import seacow
import arguments

arguments.parse_args()

game = seacow.SandboxLoop()
game.play()
