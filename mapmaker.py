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
import random
from pyglet.window import key
import gui

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



        self.background_color = [30, 30, 30]
        self.background_rect = shapes.Rect((self.width / 2, self.height / 2), self.width, self.height)
        self.background = component.Component(self.background_rect, self.background_color, pyglet.gl.GL_POLYGON)

        self.keys = dict()
        self.keys[key.A] = False

        self.mouse_visibility = True
        self.cursor_type = None
        self.cursor_pic = None
        self.cursor_pos = (0, 0)

        self.gui_button_functions = [self.change_cursor_type, self.change_cursor_type]
        self.gui_button_parameters = [["Tree", "Oak"], ["Mountain", "Snowy"]]
        self.gui_width = self.width
        self.gui_height = 50
        self.gui_color = [220, 112, 50]
        self.gui_pos = (self.width / 2, self.height - self.gui_height / 2)
        self.gui = gui.GUI(self.gui_pos, self.gui_width, self.gui_height, self.gui_color, self.gui_button_functions, self.gui_button_parameters)


        self.clock = pyglet.clock.get_default()
        self.clock.schedule(self.update_cursor)
        self.fps_display = pyglet.window.FPSDisplay(self)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.A:
            self.keys[symbol] = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        super().on_mouse_press(x, y, buttons, modifiers)
        self.layer.add_if_not_intersecting(self.make_map_object(self.cursor_pos, "Tree", "Oak"))
        if self.gui.hovered:
            self.gui.cursor_hovered(self.cursor_pos, True)

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        if self.cursor_type != None:
            self.cursor_pic = self.make_map_object(self.cursor_pos, self.cursor_type, self.cursor_subtype, True, 112)
        if self.gui.hovered:
            self.gui.cursor_hovered(self.cursor_pos)


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if self.cursor_type != None:
            self.cursor_pic = self.make_map_object(self.cursor_pos, self.cursor_type, self.cursor_subtype, True, 112)

        self.layer.add_if_not_intersecting(self.make_map_object(self.cursor_pos, "Tree", "Oak"))

    def on_draw(self):
        super().on_draw()
        self.background.vertex_list.draw(self.background.draw_type)
        self.layer.draw()
        if self.cursor_type != None and self.cursor_pic != None:
            self.cursor_pic.draw()

        self.fps_display.draw()

        self.gui.draw()

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

    def toggle_cursor_visibility(self, set_to = None):
        if set_to != None:
            self.mouse_visibility = set_to
        else:
            self.mouse_visibility = not self.mouse_visibility
        self.set_mouse_visible(self.mouse_visibility)

    def update_cursor(self, dt):
        if self.gui.contains_point(self.cursor_pos):
            self.cursor_pic = None
            self.toggle_cursor_visibility(True)
            self.gui.hovered = True
        else:
            if self.cursor_type != None:
                self.toggle_cursor_visibility(False)
            else:
                self.toggle_cursor_visibility(True)
            self.gui.hovered = False

    def change_cursor_type(self, cursor_type, cursor_subtype):
        self.cursor_type = cursor_type
        self.cursor_subtype = cursor_subtype

map_maker = Map_maker(1280, 720)
map_maker.set_caption("Map Maker")
pyglet.app.run()