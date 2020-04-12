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
import copy
import component

class Map_maker(app.App):
    def __init__(self, width, height):
        super().__init__(width, height)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

        self.layer = layer.Layer(width, height)

        self.oak_tree_leaf_color = [45, 112, 3]
        self.oak_tree_trunk_color = [112, 52, 3]

        self.rock_color = [112, 112, 112]
        self.snow_color = [255, 255, 255]

        self.set_mouse_visible(False)
        self.cursor_pic = None

        self.background_color = [30, 30, 30]
        self.background_rect = shapes.Rect((self.width / 2, self.height / 2), self.width, self.height)
        self.background = component.Component(self.background_rect, self.background_color, pyglet.gl.GL_POLYGON)

        self.fps_display = pyglet.window.FPSDisplay(self)
    
    
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.K_A:
            print('a')

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        super().on_mouse_press(x, y, buttons, modifiers)
        self.layer.add_if_not_intersecting(self.make_map_object(self.cursor_pos, "Tree", "Oak"))

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        self.cursor_pic = self.make_map_object(self.cursor_pos, "Tree", "Oak", True, 112)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.layer.add_if_not_intersecting(self.make_map_object(self.cursor_pos, "Tree", "Oak"))

    def on_draw(self):
        super().on_draw()
        self.background.vertex_list.draw(self.background.draw_type)
        self.layer.draw()
        self.cursor_pic.draw()
        
        self.fps_display.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.layer.update(width, height)
        self.background_rect = shapes.Rect((self.width / 2, self.height / 2), self.width, self.height)
        self.background = component.Component(self.background_rect, self.background_color, pyglet.gl.GL_POLYGON)

    def make_map_object(self, pos, object_type, object_subtype = None, alpha = False, alpha_value = None):
        if object_type == "Tree":
            if object_subtype == "Oak":
                leaf_color = copy.copy(self.oak_tree_leaf_color)
                trunk_color = copy.copy(self.oak_tree_trunk_color)
            if alpha:
                leaf_color.append(alpha_value)
                trunk_color.append(alpha_value)
            obj = tree.Tree(pos, 10, 20, leaf_color, trunk_color, 1)
        elif object_type == "Mountain":
            rock_color = copy.copy(self.rock_color)
            snow_color = copy.copy(self.snow_color)
            snow = False
            if object_subtype == "Snowy":
                if alpha:
                    rock_color.append(alpha_value)
                    snow_color.append(alpha_value)
                    snow = True
            obj = mountain.Mountain(pos, 80, 50, rock_color, snow, snow_color)
        return obj

    def change_cursor(self, cursor_type):
        if cursor_type == "Tree":
            pass


map_maker = Map_maker(1280, 720)
map_maker.set_caption("Map Maker")
pyglet.app.run()