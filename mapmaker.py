################################################################################
#
#   mapmaker.py
#   Code by: Casey Walker
#
################################################################################

import pyglet
import app
import layer
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

    #The following is consistent of setup functions. Most of them are called on
    #startup, and some may be called throughout the use of the program to
    #reset a portion of the map or program. It also contains values such as
    #colors and other parameters that can be changed/customized for a different
    #look/feel to the program (namely colors, widths, heights, etc)
    ############################################################################
    def setup(self):
        self.clock_setup()
        self.obj_setup()
        self.layer_setup()
        self.cursor_setup()
        self.gui_setup()

    def clock_setup(self):
        self.clock = pyglet.clock.get_default()

    def obj_setup(self):
        #These are all of the sets of arguments for "object_type" and
        #"object_subtype" that can be passed into make_map_object to receive
        #the specified object.
        self.map_obj_types = [
                            ["Tree", "Oak"],
                            ["Tree", "Spruce"],
                            ["Mountain", "Snowy"],
                            ["Hill"],
                            ["House"]
                             ]

        #These are the sets of objects that go in a given
        #region of the voronoi diagram (random map generation).
        self.voronoi_object_sets = [
                            [ ["Tree", "Oak"], ["Mountain"] ],
                            [ ["Tree", "Spruce"], ["Mountain", "Snowy"] ],
                            [ ["Tree", "Oak"], ["House"] ],
                            [ ["Tree", "Spruce"], ["House"] ],
                            [ ["Hill"] ],
                                   ]

        #For scaling objects' sizes (see on_mouse_scroll).
        self.scale = 1

        #The following are parameters for creating the map objects. They can
        #be easily changed to modify the look and colors of objects.
        #Colors are ALWAYS a list of 4 integers (0-255) --> [r, g, b, a]
        #======================================================================#
        self.oak_tree_leaf_color =  [45, 112, 3, 255]
        self.oak_tree_trunk_color = [112, 52, 3, 255]
        self.oak_tree_leaves = 1
        self.oak_tree_width = 10
        self.oak_tree_height = 20

        self.spruce_tree_leaf_color =  [30, 85, 25, 255]
        self.spruce_tree_trunk_color = [95, 60,  0, 255]
        self.spruce_tree_leaves = 2 #anything over 3 or 4 looks a little odd :P
        self.spruce_tree_width = 10
        self.spruce_tree_height = 20

        self.mountain_rock_color = [112, 112, 112, 255]
        self.mountain_snow_color = [255, 255, 255, 255]
        self.mountain_width = 30
        self.mountain_height = 40

        self.hill_color = [15, 112, 26, 255]
        self.hill_width = 5
        self.hill_height = 5

        self.lake_water_color = [0, 0, 112, 255]

        self.house_wall_color = [200, 112, 70, 255]
        self.house_door_color = [100, 70, 40, 255]
        self.house_roof_color = [80, 70, 65, 255]
        self.house_width = 10
        self.house_height = 10
        
        self.show_generation = False
        #======================================================================#

    def layer_setup(self):
        self.layer_height_percent = 0.9 #used for ratio in layer-gui making
        self.layer_width = self.width
        self.layer_height = self.height * self.layer_height_percent
        
        #Layer is split into a grid of "regions" that contain the map objects.
        self.layer_region_width = 200
        self.layer_region_height = 200
        self.layer_grid_visibility = False

        self.layer_color = [112, 200,  20, 255]

        self.layer = layer.Layer(self.layer_width,
                                 self.layer_height,
                                 self.layer_color,
                                 self.layer_region_width,
                                 self.layer_region_height)
        self.voronoi_gen_borders = None
        self.voronoi_gen_borders_color = [0, 0, 0, 255]

    def cursor_setup(self):
        #Cursor is used for selcting/moving/placing objects by holding a 
        #function to call on clicks (or drags) and arguments for it.
        self.cursor = cursor.Cursor(self)
        self.cursor.type = "Select"
        self.cursor_default_function = self.select_obj
        self.cursor_deflaut_function_args = [self.cursor.get_pos, True]
        self.cursor_default_visibility = True
        self.cursor.set_default(self.cursor_default_function, self.cursor_deflaut_function_args)

    def gui_setup(self):
        #Gui is a bar at the top of the screen with the buttons listed below
        #(that call the functions listed below).
        self.gui_width = self.width
        self.gui_height = self.height - self.layer_height
        self.gui_color = [220, 112, 50, 255]

        #Pos defines the center x and y of the gui rectangle.
        self.gui_pos = (self.width / 2, self.height - self.gui_height / 2)

        #The following contains all the contstruction properties of the gui
        #buttons. It is consistent of button call functions, parameters, colors
        #labels, and width/height.
        #======================================================================#
        # The functions for each button to call when pressed
        # (indices are parallel to the rest of the button parameters).
        self.gui_button_functions = [self.change_cursor_type, 
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.change_cursor_type,
                                     self.generate_random_map,
                                     self.clear_map,
                                     self.change_cursor_type,
                                     self.toggle_grid]

        # The arguments to be called in the ^^above^^ functions
        # (empty list implies no arguments).
        self.gui_button_args = [ 
            [ self.add_map_obj, 
              (self.cursor.get_pos, "Tree", "Oak", True),
              "Map_obj" ],

            [ self.add_map_obj,
              (self.cursor.get_pos, "Tree", "Spruce", True),
              "Map_obj" ],

            [ self.add_map_obj,
              (self.cursor.get_pos, "Mountain", "Snowy", True),
              "Map_obj" ],

            [ self.add_map_obj,
              (self.cursor.get_pos, "Hill", None, True),
              "Map_obj" ],

            [ self.add_map_obj,
              (self.cursor.get_pos, "House", None, True),
              "Map_obj" ],

            [ self.add_map_obj,
              (self.cursor.get_pos, "Lake", None,  True),
              "Map_obj" ],

            [ ],

            [ ],

            [ self.select_obj,
              (self.cursor.get_pos, True),
              "Select" ],
            
            [ ]
        ]

        # The text that shows on each button.
        self.gui_button_labels = ["Oak Tree",
                                  "Spruce Tree",
                                  "Mountain",
                                  "Hill",
                                  "House",
                                  "Lake",
                                  "Random Map",
                                  "Clear Map",
                                  "Select",
                                  "Toggle Grid"]
        
        self.gui_button_label_colors = [ [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255],
                                         [255, 255, 255, 255] ]

        # Color displayed when NOT hovered.
        self.gui_button_colors = [       [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255],
                                         [ 70,  70,  70, 255],
                                         [ 50, 112, 255, 255],
                                         [ 50, 112, 255, 255] ]

        # Color displayed WHEN hovered.
        self.gui_button_hover_colors = [ [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255],
                                         [200, 70, 200, 255],
                                         [200, 70,  70, 255],
                                         [ 90, 40, 200, 255],
                                         [ 90, 40, 200, 255] ]

        self.gui_button_numbers = len(self.gui_button_labels)
        self.gui_button_padding = 5
        self.gui_button_height = self.gui_height * .7
        self.gui_button_width = (((self.gui_width - self.gui_button_padding) / 
                                   self.gui_button_numbers) - 
                                   self.gui_button_padding)
        self.gui_button_label_font_size = 14
        self.gui_button_label_font = "Arail"
        #======================================================================#

        self.gui = gui.GUI(self.gui_pos, self.gui_width, self.gui_height,
                           self.gui_color, self.gui_button_width, self.gui_button_height, self.gui_button_padding,
                           self.gui_button_colors, self.gui_button_hover_colors,
                           self.gui_button_label_colors,
                           self.gui_button_labels, self.gui_button_label_font_size, self.gui_button_label_font,
                           self.gui_button_functions, self.gui_button_args)

    def voronoi_setup(self):
        #Be aware that if the seed number is too large, it may take
        #a very (very) long time to solve the voronoi diagram.
        #Also note that if too many seeds exist with too high padding,
        #a diagram may fail to be created.
        self.voronoi_seeds_number = 10
        self.voronoi_seeds_padding = 80
        self.voronoi_population_attempts = 300 #(see populate_seed for use)
        self.voronoi = voronoi.Voronoi(self.width, self.layer_height,
                                       self.voronoi_seeds_number, 
                                       self.voronoi_seeds_padding)
    ############################################################################

    def on_key_press(self, symbol, modifiers):
        if symbol == key.H:
            self.gui.show_help_menu(True)
        elif symbol == key.DELETE and self.cursor.type == "Select":
            self.cursor.delete_selected()
        elif symbol == key.ESCAPE:
            self.change_cursor_type(cursor.Cursor.empty_fn, None, "Default")
        elif symbol == key.S:
            self.show_generation = not self.show_generation

    def on_key_release(self, symbol, modifiers):
        if symbol == key.H:
            self.gui.show_help_menu(False)

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor.move(dx, dy)
        self.update_cursor()
        self.gui.check_hovered(self.cursor.pos)
        if self.gui.hovered:
            self.cursor.toggle_visibility(True)

    def on_mouse_press(self, x, y, button, modifiers):
        #Gui hovered, so click interacts with gui, not map
        if self.gui.hovered:
            self.gui.clicked() #gui knows where cursor is from on_mouse_motion
        else:
            self.cursor() #call the function that cursor holds


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy) #dragged means mouse moves

        #tell cursor that it's dragged (for use in selecet_obj)
        self.cursor.dragged = True

        self.cursor() #call the function that cursor holds

    def on_mouse_release(self, x, y, button, modifiers):
        #For use with functions that require different actions when dragging
        #starts versus when dragging ends (such as select_obj)
        if self.cursor.dragged:
            self.cursor.dragged = False
            self.cursor()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scale += scroll_y / 3 #div for smalling scroll increments
        if self.cursor.selected != None:
            self.cursor.selected.scale(scroll_y / 5) #div smalls increments

    def on_draw(self):
        self.layer.draw()
        self.cursor.draw()
        self.gui.draw()

    def toggle_grid(self, set_to = None):
        if set_to == None:
            self.layer_grid_visibility = not self.layer_grid_visibility
        else:
            self.layer_grid_visibility = set_to

        self.layer.toggle_grid(self.layer_grid_visibility)
        if self.layer_grid_visibility:
            if self.voronoi_gen_borders != None:
                self.voronoi_gen_borders.delete()
                self.voronoi_gen_borders = None

    #from cursor is to know if pos is given as a function that returns a pos
    #or if pos is a tuple containing (x, y)
    def add_map_obj(self, pos, obj_type, obj_subtype = None,
                    from_cursor = False):
        obj = self.make_map_obj(pos, obj_type, obj_subtype,
                                from_cursor = from_cursor)
        if self.layer.add_if_not_intersecting(obj):
            obj.place(self.layer.batch)

    def make_map_obj(self, pos, obj_type, obj_subtype = None,
                     alpha = False, alpha_value = None, from_cursor = False):
        alpha_index = 3
        if from_cursor:
            pos = pos()
        if obj_type == "Tree":
            if obj_subtype == "Oak":
                leaf_color = list(self.oak_tree_leaf_color)
                trunk_color = list(self.oak_tree_trunk_color)
                leafs = self.oak_tree_leaves
                width = self.oak_tree_width * self.scale
                height = self.oak_tree_height * self.scale
            elif obj_subtype == "Spruce":
                leaf_color = list(self.spruce_tree_leaf_color)
                trunk_color = list(self.spruce_tree_trunk_color)
                leafs = self.spruce_tree_leaves
                width = self.spruce_tree_width * self.scale
                height = self.spruce_tree_height * self.scale
            if alpha:
                leaf_color[alpha_index] = alpha_value
                trunk_color[alpha_index] = alpha_value
            obj = map_obj.Tree(pos, width, height,
                               leaf_color, trunk_color, leafs)
        elif obj_type == "Mountain":
            rock_color = list(self.mountain_rock_color)
            snow_color = list(self.mountain_snow_color)
            width = self.mountain_width * self.scale
            height = self.mountain_height * self.scale
            snow = False
            if obj_subtype == "Snowy":
                snow = True
            if alpha:
                rock_color[alpha_index] = alpha_value
                snow_color[alpha_index] = alpha_value
            obj = map_obj.Mountain(pos, width, height,
                                   rock_color, snow, snow_color)
        elif obj_type == "Hill":
            hill_color = list(self.hill_color)
            width = self.hill_width * self.scale
            height = self.hill_height * self.scale
            if alpha:
                hill_color[alpha_index] = alpha_value
            obj = map_obj.Hill(pos, width, height, hill_color)
        elif obj_type == "Lake":
            lake_color = list(self.lake_water_color)
            if alpha:
                lake_color[alpha_index] = alpha_value
            obj = map_obj.Lake(pos, 30, 30, lake_color)
        elif obj_type == "House":
            wall_color = list(self.house_wall_color)
            door_color = list(self.house_door_color)
            roof_color = list(self.house_roof_color)
            width = self.house_width * self.scale
            height = self.house_height * self.scale
            if alpha:
                wall_color[alpha_index] = alpha_value
                door_color[alpha_index] = alpha_value
                roof_color[alpha_index] = alpha_value
            obj = map_obj.House(pos, width, height, wall_color, door_color, roof_color)
        return obj

    def generate_random_map(self, dt = None):
        #Sets a voronoi diagram of seeds up (behind-the-scenes).
        if dt == None:
            self.voronoi_setup()

        #Solves the diagram of seeds using Fortune's Algorithm (see voronoi.py).
        if self.show_generation and dt == None:
            #Call this function every clock tick to iterate to next stage in
            #voronoi solving.
            self.clock.schedule(self.generate_random_map)
        elif self.show_generation:
            points = self.voronoi.solve_visually()
            if points == None: #border generation is done
                self.clock.unschedule(self.generate_random_map)
                self.populate_voronoi()
            else:
                if self.voronoi_gen_borders != None:
                    self.voronoi_gen_borders.delete()
                num_points = len(points) // 2
                vertices = ("v2f", points)
                vertices_colors = ("c4B", 
                                   self.voronoi_gen_borders_color * num_points)

                self.voronoi_gen_borders = self.layer.batch.add(
                                   num_points, pyglet.gl.GL_LINES, None,
                                   vertices, vertices_colors)
        else:
            self.voronoi.solve()

            #Adds map objects to the diagram randomly.
            self.populate_voronoi()

    def populate_voronoi(self):
        for seed in self.voronoi.seeds:
            #Each seed in a voronoi diagram has a polygonal shape around it.
            polygon = seed.get_polygon()
            seed.polygon = polygon

            #Choose a set of objects to fill with. (defined in obj_setup)
            seed.map_obj_set = random.choice(self.voronoi_object_sets)
            self.populate_seed(seed)

    def populate_seed(self, seed):
        #Get a bounding rectangle of mins and maxs to try coordinates inside.
        (min_x, max_x, min_y, max_y) = seed.polygon.get_maxs_mins()

        #Try so many placements of random coordinates.
        for _ in range(self.voronoi_population_attempts):
            obj_type = random.choice(seed.map_obj_set) #pick an object from set
            x = random.randrange(int(min_x), int(max_x) + 1) #+1 in case euqal
            y = random.randrange(int(min_y), int(max_y) + 1) #+1 in case euqal
            pos = (x, y)
            if seed.polygon.contains_point(pos):
                self.add_map_obj(pos, *obj_type) #*obj in case obj has a subtype

    def select_obj(self, pos, from_cursor = False):
        if from_cursor:
            pos = pos() #pos is given as self.cursor.get_pos
        if self.cursor.selected == None: #cursor hasn't selected anything
            obj = self.layer.get_obj_at_pos(pos)
            self.layer.remove_obj(obj)
            obj.migrate(self.cursor.batch)
            self.cursor.selected = obj
            obj.change_visibility(112)
        elif not self.cursor.dragged: #not dragged means place held object
            if self.layer.add_if_not_intersecting(self.cursor.selected):
                self.cursor.selected.change_visibility(255)
                self.cursor.selected.migrate(self.layer.batch)
                self.cursor.selected = None

    def clear_map(self):
        self.layer_setup() #layer setup will just re-make the layer and regions

    def update_cursor(self):
        if self.cursor.img != None:
            self.cursor.img.delete()
            self.cursor.img = None
        if self.cursor.type == "Map_obj":
            self.cursor.img = self.make_map_obj(*self.cursor.args[:-1], 
                                                alpha = True, alpha_value = 112,
                                                from_cursor = True)
            self.cursor.img.place(self.cursor.batch)
            self.cursor.toggle_visibility(False)

    def change_cursor_type(self, function, args, cursor_type):
        #Change the function that cursor holds (and the args).
        #Change the type, and decide if it should be visible or not.
        self.cursor.function = function
        self.cursor.args = args
        self.cursor.type = cursor_type
        if self.cursor.type == "Default":
            self.cursor.toggle_call_default(True)
            self.cursor.toggle_visibility(self.cursor_default_visibility)
        elif self.cursor.type == "Select":
            self.cursor.toggle_call_default(False)
            if not self.gui.hovered:
                self.cursor.toggle_visibility(True)
        else:
            self.cursor.toggle_call_default(False)
            if not self.gui.hovered:
                self.cursor.toggle_visibility(False)

map_maker = Map_maker(1500, 780)
map_maker.set_caption("Map Maker")
pyglet.app.run()