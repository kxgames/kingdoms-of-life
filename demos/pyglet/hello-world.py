import pyglet
import drawing
from kxg.geometry import Rectangle

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

box = Rectangle.from_dimensions(50, 100, 300, 200)
drawing.draw_rectangle(box, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
