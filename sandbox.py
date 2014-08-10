#!/usr/bin/env python3

import seacow
import arguments

arguments.parse_args()

game = seacow.SandboxLoop()
game.play()
