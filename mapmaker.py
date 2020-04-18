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
import cursor
import voronoi

class Map_maker(app.App):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.setup()

    def setup(self):
        self.oak_tree_leaf_color = [45, 112, 3]
        self.oak_tree_trunk_color = [112, 52, 3]
        self.rock_color = [112, 112, 112]
        self.snow_color = [255, 255, 255]

        self.layer_width = self.width
        self.layer_height = self.height * .95
        self.layer_color = [240, 194, 112]
        self.layer_setup()
        self.clock_setup()
        self.cursor_setup()
        self.gui_setup()

        self.voronoi_setup()

    def layer_setup(self):
        self.layer = layer.Layer(self.layer_width, self.layer_height, self.layer_color)

    def cursor_setup(self):
        self.cursor = cursor.Cursor(None, None)

    def gui_setup(self):
        self.gui_button_functions = [self.change_cursor_type, 
                                     self.change_cursor_type]
        self.gui_button_parameters = [ 
            [
                self.add_map_obj, 
                (self.cursor.get_pos, "Tree", "Oak", True),
                "Map_obj"
                ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "Mountain", "Snowy", True),
                "Map_obj"
                ] 
        ]
        self.gui_button_labels = ["Tree",
                                  "Mountain"]
        self.gui_button_label_colors = [ [255, 255, 255, 255],
                                         [255, 255, 255, 255] ]
        self.gui_button_colors = [ [50, 112, 255],
                                   [50, 112, 255] ]
        self.gui_width = self.width
        self.gui_height = self.height - self.layer_height
        self.gui_color = [220, 112, 50]
        self.gui_pos = (self.width / 2, self.height - self.gui_height / 2)
        self.gui = gui.GUI(self.gui_pos, self.gui_width, self.gui_height,
                           self.gui_color, self.gui_button_functions,
                           self.gui_button_parameters, self.gui_button_labels,
                           self.gui_button_colors, self.gui_button_label_colors)

    def clock_setup(self):
        self.clock = pyglet.clock.get_default()
        self.clock.schedule(self.clock_ticked)

    def voronoi_setup(self):
        self.voronoi = voronoi.Voronoi(10, (100, 400), (100, 400), [255, 255, 255, 50])

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.gui.show_help_menu(True)
            self.voronoi_setup()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.gui.show_help_menu(False)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)
        self.cursor.pos = (x, y)
        self.voronoi.increase_radii(scroll_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        super().on_mouse_press(x, y, buttons, modifiers)
        self.cursor()
        if self.gui.hovered:
            self.gui.cursor_hovered(self.cursor_pos, True)

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        self.cursor.pos = (x, y)
        if self.gui.hovered:
            self.gui.cursor_hovered(self.cursor.pos)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.cursor.pos = (x, y)
        self.cursor()

    def on_draw(self):
        super().on_draw()
        self.layer.draw()
        self.gui.draw()
        self.cursor.draw()
        self.voronoi.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)

    def add_map_obj(self, pos, obj_type, obj_subtype, from_cursor = False):
        obj = self.make_map_obj(pos, obj_type, obj_subtype, from_cursor = from_cursor)
        self.layer.add_if_not_intersecting(obj)

    def make_map_obj(self, pos, obj_type, obj_subtype, alpha = False, alpha_value = None, from_cursor = False):
        if from_cursor:
            pos = pos()
        if obj_type == "Tree":
            if obj_subtype == "Oak":
                leaf_color = copy.copy(self.oak_tree_leaf_color)
                trunk_color = copy.copy(self.oak_tree_trunk_color)
            if alpha:
                leaf_color.append(alpha_value)
                trunk_color.append(alpha_value)
            obj = tree.Tree(pos, 10, 20, leaf_color, trunk_color, 1)
        elif obj_type == "Mountain":
            rock_color = copy.copy(self.rock_color)
            snow_color = copy.copy(self.snow_color)
            snow = False
            if obj_subtype == "Snowy":
                snow = True
            if alpha:
                rock_color.append(alpha_value)
                snow_color.append(alpha_value)
            obj = mountain.Mountain(pos, 30, 30, rock_color, snow, snow_color)
        return obj

    def toggle_cursor_visibility(self, set_to = None):
        self.cursor.toggle_visibility(set_to)
        self.set_mouse_visible(self.cursor.visibility)

    def clock_ticked(self, dt):
        self.update_cursor()
        if self.gui.hovered:
            self.gui.cursor_hovered(self.cursor.pos)

    def update_cursor(self):
        if self.gui.has_cursor(self.cursor.pos):
            self.toggle_cursor_visibility(True)
            self.cursor.toggle_img_visibility(False)
            self.gui.hovered = True
        elif self.cursor.type != None:
            self.cursor.toggle_img_visibility(True)
            self.toggle_cursor_visibility(False)
            self.gui.hovered = False
        if self.cursor.type == "Map_obj":
            self.cursor.img = self.make_map_obj(*self.cursor.args[:-1], True, 112, True)

    def change_cursor_type(self, function, args, cursor_type):
        self.cursor.function = function
        self.cursor.args = args
        self.cursor.type = cursor_type

map_maker = Map_maker(1280, 720)
map_maker.set_caption("Map Maker")
pyglet.app.run()