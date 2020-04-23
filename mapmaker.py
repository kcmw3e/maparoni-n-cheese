################################################################################
#
#   mapmaker.py
#   Code by: Casey Walker
#
################################################################################

import pyglet
import app
import shapes
import layer
import copy
import random
from pyglet.window import key
import gui
import cursor
import voronoi
import map_obj

class Map_maker(app.App):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.setup()

    def setup(self):
        self.map_obj_types = [ ["Tree", "Oak"],
                               ["Tree", "Spruce"],
                               ["Mountain", "Snowy"],
                               ["Hill"],
                               ["Lake"],
                               ["House"] ]
        self.voronoi_object_sets = [
                                    [ ["Tree", "Oak"], ["Mountain"] ],
                                    [ ["Tree", "Spruce"], ["Mountain", "Snowy"] ],
                                    [ ["Tree", "Oak"], ["House"] ],
                                    [ ["Tree", "Spruce"], ["House"] ],
                                    [ ["Hill"] ],
                                   ]

        self.oak_tree_leaf_color = [45, 112, 3]
        self.oak_tree_trunk_color = [112, 52, 3]

        self.spruce_tree_leaf_color = [29, 84, 24]
        self.spruce_tree_trunk_color = [94, 60, 2]

        self.rock_color = [112, 112, 112]
        self.snow_color = [255, 255, 255]

        self.hill_color = [33, 125, 26]

        self.lake_water_color = [0, 0, 180]

        self.house_wall_color = [201, 116, 66]
        self.house_door_color = [89, 68, 40]
        self.house_roof_color = [77, 72, 65]

        self.layer_setup()
        self.clock_setup()
        self.cursor_setup()
        self.gui_setup()

    def layer_setup(self):
        self.layer_percent = 0.9
        self.layer_width = self.width
        self.layer_height = self.height * self.layer_percent
        self.layer_color = [240, 194, 112]
        self.layer_color = [136, 189, 23]
        self.layer = layer.Layer(self.layer_width, self.layer_height, self.layer_color)

    def cursor_setup(self):
        self.cursor = cursor.Cursor(None, None)

    def gui_setup(self):
        self.gui_button_functions = [self.change_cursor_type, 
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.generate_random_map]
        self.gui_button_parameters = [ 
            [
                self.add_map_obj, 
                (self.cursor.get_pos, "Tree", "Oak", True),
                "Map_obj"
            ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "Tree", "Spruce", True),
                "Map_obj"
            ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "Mountain", "Snowy", True),
                "Map_obj"
            ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "Hill", None, True),
                "Map_obj"
            ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "Lake", None, True),
                "Map_obj"
            ],
            [
                self.add_map_obj,
                (self.cursor.get_pos, "House", None, True),
                "Map_obj"
            ],
            [
                
            ]
        ]
        self.gui_button_labels = ["Oak Tree",
                                  "Spruce Tree",
                                  "Mountain",
                                  "Hill",
                                  "Lake",
                                  "House",
                                  "Random Map"]
        self.gui_button_label_colors = [ [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255] ]
        self.gui_button_colors = [ [50, 112, 255],
                                   [50, 112, 255],
                                   [50, 112, 255],
                                   [50, 112, 255],
                                   [50, 112, 255],
                                   [50, 112, 255],
                                   [50, 112, 255] ]
        self.gui_button_hover_colors = [ [92, 39, 217],
                                         [92, 39, 217],
                                         [92, 39, 217],
                                         [92, 39, 217],
                                         [92, 39, 217],
                                         [92, 39, 217],
                                         [92, 39, 217] ]
        self.gui_width = self.width
        self.gui_height = self.height - self.layer_height
        self.gui_color = [220, 112, 50]
        self.gui_pos = (self.width / 2, self.height - self.gui_height / 2)
        self.gui = gui.GUI(self.gui_pos, self.gui_width, self.gui_height,
                           self.gui_color, self.gui_button_functions,
                           self.gui_button_parameters, self.gui_button_labels,
                           self.gui_button_colors, self.gui_button_label_colors,
                           self.gui_button_hover_colors)

    def clock_setup(self):
        self.clock = pyglet.clock.get_default()
        self.clock.schedule(self.clock_ticked)

    def voronoi_setup(self):
        self.voronoi_seeds_number = 10
        self.voronoi_seeds_padding = 10
        self.voronoi = voronoi.Voronoi(self.width, self.layer_height, self.voronoi_seeds_number, self.voronoi_seeds_padding)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.gui.show_help_menu(True)
            self.voronoi_setup()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.gui.show_help_menu(False)
        if symbol == key.SPACE:
            self.voronoi.solve()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)
        self.cursor.pos = (x, y)

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
        self.voronoi_batch.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)

    def add_map_obj(self, pos, obj_type, obj_subtype = None, from_cursor = False):
        obj = self.make_map_obj(pos, obj_type, obj_subtype, from_cursor = from_cursor)
        self.layer.add_if_not_intersecting(obj)

    def make_map_obj(self, pos, obj_type, obj_subtype = None, alpha = False, alpha_value = None, from_cursor = False):
        if from_cursor:
            pos = pos()
        if obj_type == "Tree":
            if obj_subtype == "Oak":
                leaf_color = copy.copy(self.oak_tree_leaf_color)
                trunk_color = copy.copy(self.oak_tree_trunk_color)
                leafs = 1
            elif obj_subtype == "Spruce":
                leaf_color = copy.copy(self.spruce_tree_leaf_color)
                trunk_color = copy.copy(self.spruce_tree_trunk_color)
                leafs = 2
            if alpha:
                leaf_color.append(alpha_value)
                trunk_color.append(alpha_value)
            obj = map_obj.Tree(pos, 10, 20, leaf_color, trunk_color, leafs)
        elif obj_type == "Mountain":
            rock_color = copy.copy(self.rock_color)
            snow_color = copy.copy(self.snow_color)
            snow = False
            if obj_subtype == "Snowy":
                snow = True
            if alpha:
                rock_color.append(alpha_value)
                snow_color.append(alpha_value)
            obj = map_obj.Mountain(pos, 30, 30, rock_color, snow, snow_color)
        elif obj_type == "Hill":
            hill_color = copy.copy(self.hill_color)
            if alpha:
                hill_color.append(alpha_value)
            obj = map_obj.Hill(pos, 10, 10, hill_color)
        elif obj_type == "Lake":
            lake_color = copy.copy(self.lake_water_color)
            if alpha:
                lake_color.append(alpha_value)
            obj = map_obj.Lake(pos, 30, 30, lake_color)
        elif obj_type == "House":
            wall_color = copy.copy(self.house_wall_color)
            door_color = copy.copy(self.house_door_color)
            roof_color = copy.copy(self.house_roof_color)
            if alpha:
                wall_color.append(alpha_value)
                door_color.append(alpha_value)
                roof_color.append(alpha_value)
            obj = map_obj.House(pos, 20, 15, wall_color, door_color, roof_color)
        return obj

    def generate_random_map(self):
        self.voronoi_setup()
        self.voronoi.solve()
        self.voronoi_batch = pyglet.graphics.Batch()
        self.populate_voronoi()

    def populate_voronoi(self):
        self.voronoi_polygons = dict()
        for seed in self.voronoi.seeds:
            polygon = seed.get_polygon()
            points = polygon.lines_points
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = [r,g,b]
            #self.voronoi_batch.add(len(points) // 2, pyglet.gl.GL_LINES, None, ("v2f", points), ("c3B", len(points) // 2 * color))
            seed.polygon = polygon
            seed.map_obj_set = random.choice(self.voronoi_object_sets)
            seed.unpopulated = True
            self.populate_seed(seed)

    def populate_seed(self, seed):
        (min_x, max_x, min_y, max_y) = seed.polygon.get_maxs_and_mins()
        for _ in range(300):
            obj_type = random.choice(seed.map_obj_set)
            x = random.randrange(int(min_x), int(max_x) + 1) #+1 in case euqal
            y = random.randrange(int(min_y), int(max_y) + 1) #+1 in case euqal
            pos = (x, y)
            if seed.polygon.contains_point(pos):
                self.add_map_obj(pos, *obj_type)

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