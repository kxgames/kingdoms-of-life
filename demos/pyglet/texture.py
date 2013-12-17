#!/usr/bin/env python

# For now, only make a simplified flat map with three types: Land, 
# Water, and Mountain.

class Map:
    def __init__(self):
        self.size = (0,0)
        self.tile_width = 64
        self.tiles = None

    def setup(self, n_cols, n_rows):
        self.size = (n_cols, n_rows)

        self.generate_simple()
        #self.generate_wander()

    def generate_simple(self):
        n_cols, n_rows = self.size
        self.tiles = [[ Tile() for x in range(n_cols)] for y in range(n_rows)]
        for x in range(n_cols):
            for y in range(n_rows//2):
                if x < n_cols//2:
                    self.tiles[y][x].land_type = 'Water'
                else:
                    self.tiles[y+n_rows//2+n_rows%2][x].land_type = 'Mountain'


    def get_type(self, col, row):
        return self.tiles[row][col].land_type


class Tile:
    def __init__(self):
        self.land_type = 'Land'

if __name__ == '__main__':
    import ctypes
    import pyglet
    import pyglet.gl as gl

    bin = pyglet.image.atlas.TextureBin()

    def path_to_array(path):
        from matplotlib.pyplot import imread
        buffer = 255 * imread(path)
        buffer = buffer.astype('uint8')
        return buffer

    def array_to_texture(buffer):
        width, height = buffer.shape[0:2]
        data, stride = buffer.tostring(), -buffer.strides[0]
        image = pyglet.image.ImageData(width, height, 'RGBA', data, stride) 
        return bin.add(image)

    def load_image(path):
        buffer = path_to_array(path)

        return array_to_texture(buffer)

    # Run tests
    map = Map()
    map.setup(25,25)

    batch = pyglet.graphics.Batch()

    #grass_img = pyglet.image.load('images/map/grass-64-res.png')

    #grass_img = pyglet.image.load('images/map/grass-64-res.png').get_data('ub', 64)
    #texture_id = gl.glGenTextures(1, ctypes.byref(gl.GLuint()))
    #gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    #gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, 64, 64, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, grass_img)
    #
    #grass_tex = grass_img.get_texture()

    size = map.size
    width = map.tile_width
    offset = width / 2.0
    icon = load_image('grass-64-res.png')
    tile_sprites = []

    for tile_x in range(size[0]):
        for tile_y in range(size[1]):
            dx,dy = -offset, -offset
            x = tile_x * width + dx
            y = tile_y * width + dy
            tile_sprites.append(pyglet.sprite.Sprite(
                    icon,
                    x=x, y=y,
                    batch=batch))

    #vertex_count = 4 * size[0] * size[1]

    #gl.glEnable(grass_tex.target)
    #gl.glBindTexture(grass_tex.target, grass_tex.id)

    #vlist = batch.add(4, gl.GL_QUADS, None, 'v2f', 't2f')
    #
    #vlist.vertices[0:8] = [0,0, 320,0, 320,320, 0,320]
    #vlist.tex_coords[0:8] = [0,0, 1,0, 1,1, 0,1]
    #    
    ##self.vertex_list = batch.add(vertex_count, GL_QUADS, layer, 'v2f', 't2f')

    ##for tile_x in range(size[0]):
    ##    for tile_y in range(size[1]):
    ##        # i initially is the first position of the tile in the 
    ##        # 2D vertex list. The corner for loop increments i by 2 
    ##        # because each coordinate takes two spots in the vertex 
    ##        # list.
    ##        i = 2 * (4 * (y * size[0] + x) + corner)

    ##        tile_type = self.map.get_type(tile_x, tile_y)
    ##        pyglet.gl.glBindTexture(grass_tex.target, grass_tex.id)
    ##        for corner in (-1,-1), (1,-1), (1,1), (-1,1):
    ##            dx,dy = corner
    ##            x = tile_x + dx * tile_half_width
    ##            y = tile_y + dy * tile_half_width
    ##            vlist.vertices[i:i+2] = [x, y]

    ##            tx, ty = corner
    ##            tx = (tx + 1) / 2.0
    ##            ty = (ty + 1) / 2.0
    ##            vlist.tex_coords[i:i+2] = [tx,ty]

    ##            i += 2;

    #pyglet.gl.glDisable(grass_tex.target)

    window = pyglet.window.Window(320,320)

    @window.event
    def on_draw():
        batch.draw()


    pyglet.app.run()

