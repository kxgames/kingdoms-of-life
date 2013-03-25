#!/usr/bin/env python

from __future__ import division

import os, sys
import random
import pygame
import pygame.gfxdraw

from math import *
from pygame import *

os.chdir('..')

pygame.init()

black = 0, 0, 0
orange = 255, 102, 0
green = 0, 128, 0
white = 255, 255, 255
transparent = 0, 0, 0, 0

screen = pygame.display.set_mode((100, 100))
screen.fill(white)

class ClippingMask:

    def __init__(self, path):
        self.mask = pygame.image.load(path)
        self.size = self.mask.get_size()

        width, height = self.mask.get_size()
        array = pygame.PixelArray(self.mask)

        for x in range(width):
            for y in range(height):
                intensity = self.mask.unmap_rgb(array[x][y]).r
                array[x][y] = 255, 255, 255, intensity

    def apply(self, surface):
        origin = 0, 0
        blend_mode = pygame.BLEND_RGBA_MULT
        per_pixel_alpha = pygame.SRCALPHA

        assert surface.get_flags() & per_pixel_alpha
        surface.blit(self.mask, origin, special_flags=blend_mode)

        return surface

    def apply_color(self, color):
        size = self.mask.get_size()
        per_pixel_alpha = pygame.SRCALPHA

        surface = Surface(size, flags=per_pixel_alpha)
        surface.fill(color)

        return self.apply(surface)


class CommunitySymbol:

    # Data (fold)
    masks = {
            'normal shape': ClippingMask('images/normal-shape.png'),
            'battle shape': ClippingMask('images/battle-shape.png'),
            'city icon':    ClippingMask('images/city-icon.png'),
            'army icon':    ClippingMask('images/army-icon.png'),
            'full health':  ClippingMask('images/full-health.png'),
            'empty health': ClippingMask('images/empty-health.png') }

    layers = {
            'normal shape': None,
            'battle shape': None,
            'city icon':    masks['city icon'].apply_color(white),
            'army icon':    masks['army icon'].apply_color(white),
            'empty health': masks['empty health'].apply_color(white) }

    font = pygame.font.Font('fonts/DejaVuSans-Bold.ttf', 16)

    def __init__(self, color):
        normal_shape_mask = self.masks['normal shape']
        battle_shape_mask = self.masks['battle shape']

        self.layers['normal shape'] = normal_shape_mask.apply_color(color)
        self.layers['battle shape'] = battle_shape_mask.apply_color(color)

        self.level = 5
        self.health = 0.5
        self.shape = self.layers['normal shape']
        self.icon = self.layers['city icon']
        self.position = 10, 10

    def draw(self, screen):
        self.draw_shape(screen)
        self.draw_icon(screen)
        self.draw_level(screen)
        self.draw_health(screen)

    def draw_shape(self, screen):
        screen.blit(self.shape, self.position)

    def draw_icon(self, screen):
        screen.blit(self.icon, self.position)

    def draw_level(self, screen):
        level = self.font.render(str(self.level), True, white);
        level_x = 40.000 + self.position[0] - level.get_width() / 2
        level_y = 32.015 + self.position[1] - level.get_height() / 2
        level_position = level_x, level_y

        screen.blit(level, level_position)

    def draw_health(self, screen):
        full_health = self.masks['full health']
        empty_health = self.layers['empty health']

        health_wedge = Surface(full_health.size, flags=pygame.SRCALPHA)
        health_wedge.fill(transparent)

        iterations = 50
        cx, cy = health_wedge.get_size()
        cx /= 2; cy /= 2
        points = [(cx, cy)]

        for i in range(iterations + 1):
            x = cx * (1 - cos(self.health * pi * i / iterations))
            y = cy * (1 - sin(self.health * pi * i / iterations))
            points.append((int(x), int(y)))

        pygame.draw.polygon(health_wedge, white, points)

        full_health.apply(health_wedge)

        screen.blit(health_wedge, self.position)
        screen.blit(empty_health, self.position)

    def set_level(self, level):
        if level and level in '123456789':
            self.level = level

    def increment_health(self, delta):
        self.health = min(self.health + delta, 1)

    def decrement_health(self, delta):
        self.health = max(self.health - delta, 0)

    def toggle_shape(self):
        if self.shape is self.layers['normal shape']:
            self.shape = self.layers['battle shape']
        else:
            self.shape = self.layers['normal shape']

    def toggle_icon(self):
        if self.icon is self.layers['city icon']:
            self.icon = self.layers['army icon']
        else:
            self.icon = self.layers['city icon']



symbol = CommunitySymbol(green)

while True:
    screen.fill(white)
    symbol.draw(screen)
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            raise SystemExit

        if event.type == KEYDOWN:
            symbol.set_level(event.unicode)

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                symbol.toggle_shape()

            if event.button == 3:
                symbol.toggle_icon()

            if event.button == 4:
                symbol.increment_health(0.05)

            if event.button == 5:
                symbol.decrement_health(0.05)

