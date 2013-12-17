#!/usr/bin/env python

# For now, only make a simplified flat map with three types: Land, 
# Water, and Mountain.

import kxg
from kxg.geometry import Vector

class Map(kxg.Token, kxg.geometry.Rectangle):
    def __init__(self, n_cols, n_rows, tile_width):
        kxg.Token.__init__(self);
        kxg.geometry.Rectangle.__init__(self, 0, 0, n_cols * tile_width, n_rows * tile_width)

        self.array_size = (n_cols, n_rows)
        self.tile_width = tile_width
        self.tiles = None
        self.directions = {
                'N' : Vector( 0,  1),
                'S' : Vector( 0, -1),
                'E' : Vector( 1,  0),
                'W' : Vector(-1,  0)
                }

        print "Map created with dimensions ", self.array_size

    def __extend__(self):
        return {'gui': gui.MapExtension}

    def setup(self):
        self.generate_simple()
        #self.generate_wander()

    def generate_simple(self):
        n_cols, n_rows = self.array_size
        self.tiles = [[ Tile() for x in range(n_cols)] for y in range(n_rows)]
        for x in range(n_cols):
            for y in range(n_rows//2):
                if x < n_cols//2:
                    self.tiles[y][x].land_type = 'Water'
                else:
                    self.tiles[y+n_rows//2+n_rows%2][x].land_type = 'Mountain'

    def generate_wander(self):
        n_cols, n_rows = self.array_size
        self.tiles = [[ Tile() for x in range(n_cols)] for y in range(n_rows)]

        #chains_per_type = 5
        #wander_circle_distance = 50
        #wander_circle_radius = 30
        #step_distance = 30
        #steps_per_chain = 5
        #step_radius = 40
        ## Place clusters of land types.
        #for type in 'Water', 'Mountain'

        #    # Make the starting point of the chain.
        #    for x in range(self.chains_per_type):
        #        center = Vector.inside_box(self.array_size)
        #        heading = Vector.random()

        #        # Create the deposits randomly in the step's circle.
        #        for y in range(self.steps_per_chain):
        #            for 

        #            # Move to the next step in the chain.
        #            target = Vector.random() * self.wander_circle_radius
        #            target_offset = heading * self.wander_circle_distance
        #            target_vector = target + target_offset
        #            heading += target_vector.get_normal()
        #            heading = heading.get_normal()
        #            center += heading * self.step_distance


    def get_type(self, position):
        return self.get_tile(int(position[0]), int(position[1]))

    def get_type(self, col, row):
        return self.tiles[row][col].land_type


class Tile:
    def __init__(self):
        self.land_type = 'Land'

if __name__ == '__main__':
    import ctypes
    import pyglet
    import pyglet.gl as gl

    # Run tests
    map = Map()
    map.setup(25,25)

    batch = pyglet.graphics.Batch()

    #grass_img = pyglet.image.load('images/map/grass-64-res.png')

    grass_img = pyglet.image.load('images/map/grass-64-res.png').get_data('ub', 64)
    texture_id = gl.glGenTextures(1, ctypes.byref(gl.GLuint()))
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, 64, 64, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, grass_img)
    
    grass_tex = grass_img.get_texture()

    size = map.array_size
    tile_width = map.tile_width
    tile_half_width = tile_width / 2.0

    vertex_count = 4 * size[0] * size[1]

    gl.glEnable(grass_tex.target)
    gl.glBindTexture(grass_tex.target, grass_tex.id)

    vlist = batch.add(4, gl.GL_QUADS, None, 'v2f', 't2f')
    
    vlist.vertices[0:8] = [0,0, 320,0, 320,320, 0,320]
    vlist.tex_coords[0:8] = [0,0, 1,0, 1,1, 0,1]
        
    #self.vertex_list = batch.add(vertex_count, GL_QUADS, layer, 'v2f', 't2f')

    #for tile_x in range(size[0]):
    #    for tile_y in range(size[1]):
    #        # i initially is the first position of the tile in the 
    #        # 2D vertex list. The corner for loop increments i by 2 
    #        # because each coordinate takes two spots in the vertex 
    #        # list.
    #        i = 2 * (4 * (y * size[0] + x) + corner)

    #        tile_type = self.map.get_type(tile_x, tile_y)
    #        pyglet.gl.glBindTexture(grass_tex.target, grass_tex.id)
    #        for corner in (-1,-1), (1,-1), (1,1), (-1,1):
    #            dx,dy = corner
    #            x = tile_x + dx * tile_half_width
    #            y = tile_y + dy * tile_half_width
    #            vlist.vertices[i:i+2] = [x, y]

    #            tx, ty = corner
    #            tx = (tx + 1) / 2.0
    #            ty = (ty + 1) / 2.0
    #            vlist.tex_coords[i:i+2] = [tx,ty]

    #            i += 2;

    pyglet.gl.glDisable(grass_tex.target)

    window = pyglet.window.Window(320,320)

    @window.event
    def on_draw():
        batch.draw()


    pyglet.app.run()

