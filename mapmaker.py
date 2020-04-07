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

class Map_maker(app.App):
    def __init__(self):
        super().__init__()
        self.layer = list()

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        super().on_mouse_press(x, y, buttons, modifiers)
        self.add_tree("Oak")

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        #self.tree = tree.Tree(self.cursor_pos, 30, 40, [45, 112, 3], [112, 52, 3], 1)
        self.tree = mountain.Mountain(self.cursor_pos, 80, 50, [112, 112, 112], True, [255, 255, 255])

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.add_tree("Oak")

    def on_draw(self):
        super().on_draw()
        for t in self.layer:
            t.draw()
        self.tree.draw()

    def add_tree(self, tree_type):
        if tree_type == "Oak":
            #t = tree.Tree(self.cursor_pos, 30, 40, [45, 112, 3], [112, 52, 3], 1)
            t = mountain.Mountain(self.cursor_pos, 80, 50, [112, 112, 112], True, [255, 255, 255])
            for other in self.layer:
                if is_near(other, t, 50): #*
                    if t.intersects(other):
                        return False
            self.layer.append(t)

def is_near(a, b, near): #*
    p1 = a.pos
    p2 = b.pos
    if abs(p1[0] - p2[0]) < near or abs(p1[1] - p2[1]) < near:
        return True


map_maker = Map_maker()

pyglet.app.run()