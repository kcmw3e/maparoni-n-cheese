################################################################################
#
#   mapmaker.py
#   Code by: Casey Walker
#
################################################################################

import pyglet
import app
import tree
import mountain
import shapes
import layer

class Map_maker(app.App):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.layer = layer.Layer(width, height)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        super().on_mouse_press(x, y, buttons, modifiers)
        self.add_tree("Oak")

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        self.tree = tree.Tree(self.cursor_pos, 10, 20, [45, 112, 3, 112], [112, 52, 3, 112], 1)
        #self.tree = mountain.Mountain(self.cursor_pos, 80, 50, [112, 112, 112, 112], True, [255, 255, 255, 112])

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.tree = tree.Tree(self.cursor_pos, 10, 20, [45, 112, 3, 112], [112, 52, 3, 112], 1)
        #self.tree = mountain.Mountain(self.cursor_pos, 80, 50, [112, 112, 112, 112], True, [255, 255, 255, 112])
        self.add_tree("Oak")

    def on_draw(self):
        super().on_draw()
        self.layer.draw()
        self.tree.draw()

    def add_tree(self, tree_type):
        if tree_type == "Oak":
            t = tree.Tree(self.cursor_pos, 10, 20, [45, 112, 3], [112, 52, 3], 1)
            #t = mountain.Mountain(self.cursor_pos, 80, 50, [112, 112, 112], True, [255, 255, 255])
            self.layer.add_if_not_intersecting(t)


map_maker = Map_maker(1200, 740)
map_maker.set_caption("Map Maker")
pyglet.app.run()