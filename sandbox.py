#!/usr/bin/env python

import armedcat
import arguments

arguments.parse_args()

game = armedcat.SandboxLoop()
game.play()
