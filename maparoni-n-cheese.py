################################################################################
#
#   maparoni-n-cheese.py
#   Code by: Casey Walker
#
################################################################################

import random

import pyglet
from pyglet.window import key

import app
import cursor
import fileio
import gui
import layer
import map_obj
import voronoi

#Some notes before you run:
#   1) Just about anything can be customized from the button order to the
#      color of a map object to the size of an object. Feel free to experiment
#      with it and change some thigns around.
#   2) There are 3 keybinds to take note of
#      (2 of which are the only way to use certain features)
#       --  s  --> changes whether or not to visualize random map generation
#       -- del --> deletes a selected item
#       -- esc --> sets cursor to use select mode
#   3) There's already a note about this, but be careful when changing
#      the number of seeds and the seed padding for map generation. It can take
#      a long time to compute seeds over 60 or so (depending on your machine)
#   4) File io is basic and not fully tested, so ONLY SAVE/LOAD FILES YOU KNOW.
#      In other words, if it's not a .txt file that you've saved directly from
#      this program or that you've expressly written for this program, I highly
#      recommend you don't touch it with this program. Similarly, don't try to
#      load files that arent formatted/made for this program, ESPECIALLY
#      if they aren't .txt files.

class Map_maker(app.App):
    def __init__(self, width = 1800, height = 950):
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
        self.oak_tree_width = 15
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
        self.hill_radius = 5

        self.lake_water_color = [0, 0, 112, 255]
        self.lake_radius = 10

        self.house_wall_color = [200, 112, 70, 255]
        self.house_door_color = [112, 70, 40, 255]
        self.house_roof_color = [80, 70, 65, 255]
        self.house_width = 10
        self.house_height = 10

        #If voronoi generation should be visible
        #(runs a little slower but looks really cool)
        #(see on_key_press for toggle)
        self.show_generation = True
        #======================================================================#

    def layer_setup(self):
        self.layer_height_percent = 0.9 #used for ratio in layer-gui making
        self.layer_width = self.width
        self.layer_height = self.height * self.layer_height_percent

        #Layer is split into a grid of "regions" that contain the map objects.
        self.layer_region_width = 200
        self.layer_region_height = 200
        self.layer_grid_visibility = False #toggles with toggle_grid
        self.layer_color = [112, 200,  20, 255]

        self.layer = layer.Layer(self.layer_width,
                                 self.layer_height,
                                 self.layer_color,
                                 self.layer_region_width,
                                 self.layer_region_height)

    def cursor_setup(self):
        #Cursor is used for selcting/moving/placing objects by holding a 
        #function and arguments to call on clicks (or drags).
        self.cursor = cursor.Cursor(self)

        #Default settings for cursor (see on_key_press to toggle call_default).
        self.cursor_default_type = "Select"
        self.cursor_default_function = self.select_obj
        self.cursor_deflaut_function_args = [self.cursor.get_pos, True]
        self.cursor_default_visibility = True
        self.cursor.set_default(self.cursor_default_function,
                                self.cursor_deflaut_function_args,
                                self.cursor_default_type)

        self.cursor_selection_visibility = 112 #used in select_obj

    def gui_setup(self):
        #Gui is a bar at the top of the screen with the buttons listed below
        #(that call the functions listed below).
        self.gui_width = self.width
        self.gui_height = self.height - self.layer_height
        self.gui_color = [0, 80, 40, 255]

        #Pos defines the center x and y of the gui rectangle.
        #This sets gui at the top of the screen.
        self.gui_pos = (self.width / 2, self.height - self.gui_height / 2)

        #The following contains all the contstruction properties of the gui
        #buttons. It is consistent of button call functions, parameters, colors
        #labels, and width/height.
        #======================================================================#
        # The text that shows on each button.
        self.gui_button_labels = ["Select",
                                  "Oak Tree",
                                  "Spruce Tree",
                                  "Mountain",
                                  "Hill",
                                  "House",
                                  "Lake",
                                  "Random Map",
                                  "Clear Map",
                                  "Toggle Grid",
                                  "Save",
                                  "Load"]

        # The functions for each button to call when pressed
        # (indices are parallel to the rest of the button parameters).
        self.gui_button_functions = [self.change_cursor_type,  #select
                                     self.change_cursor_type,  #oak
                                     self.change_cursor_type,  #spruce
                                     self.change_cursor_type,  #mtn
                                     self.change_cursor_type,  #hill
                                     self.change_cursor_type,  #house
                                     self.change_cursor_type,  #lake
                                     self.generate_random_map, #rand map
                                     self.clear_map,           #clr map
                                     self.toggle_grid,         #tog grid
                                     self.get_save_string,     #save
                                     self.load_from_string]    #load

        # The arguments to be called in the ^^above^^ functions
        # (empty list implies no arguments).
        self.gui_button_args = [ 

            [ self.select_obj,
              (self.cursor.get_pos, True),
              "Select" ],

            #Format of function change_cursor_type -->    #
            [ self.add_map_obj,                           #func for cursor click
              (self.cursor.get_pos, "Tree", "Oak", True), #^^args for func
              "Map_obj" ],                                #new cursor type

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

            
            [ ],

            [ ],

            [ ]
        ]

        self.gui_button_label_colors = [       [  0,   0,   0, 255],  #select
                                               [255, 255, 255, 255],  #oak
                                               [255, 255, 255, 255],  #spruce
                                               [255, 255, 255, 255],  #mtn
                                               [255, 255, 255, 255],  #hill
                                               [255, 255, 255, 255],  #house
                                               [255, 255, 255, 255],  #lake
                                               [255, 255, 255, 255],  #rand map
                                               [255, 255, 255, 255],  #clr map
                                               [255, 255, 255, 255],  #tog grid
                                               [255, 255, 255, 255],  #save
                                               [255, 255, 255, 255] ] #load

        self.gui_button_label_hover_colors = [ [255, 255, 255, 255],  #select
                                               [255, 255, 255, 255],  #oak
                                               [255, 255, 255, 255],  #spruce
                                               [255, 255, 255, 255],  #mtn
                                               [255, 255, 255, 255],  #hill
                                               [255, 255, 255, 255],  #house
                                               [255, 255, 255, 255],  #lake
                                               [255, 255, 255, 255],  #rand map
                                               [255, 255, 255, 255],  #clr map
                                               [255, 255, 255, 255],  #tog grid
                                               [255, 255, 255, 255],  #save
                                               [255, 255, 255, 255] ] #load

        # Color displayed when NOT hovered.
        self.gui_button_colors = [             [230, 230, 230, 255],  #select
                                               [  5,  80, 112, 255],  #oak
                                               [  5,  80, 112, 255],  #spruce
                                               [  5,  80, 112, 255],  #mtn
                                               [  5,  80, 112, 255],  #hill
                                               [  5,  80, 112, 255],  #house
                                               [  5,  80, 112, 255],  #lake
                                               [ 50,  50,  50, 255],  #rand map
                                               [ 50,  50,  50, 255],  #clr map
                                               [ 50,  50,  50, 255],  #tog grid
                                               [ 50,  50,  50, 255],  #save
                                               [ 50,  50,  50, 255] ] #load

        # Color displayed WHEN hovered.
        self.gui_button_hover_colors = [       [ 50,  50,  50, 255],  #select
                                               [  6,  98, 138, 255],  #oak
                                               [  6,  98, 138, 255],  #spruce
                                               [  6,  98, 138, 255],  #mtn
                                               [  6,  98, 138, 255],  #hill
                                               [  6,  98, 138, 255],  #house
                                               [  6,  98, 138, 255],  #lake
                                               [152,  33, 158, 255],  #rand map
                                               [189,  28,  28, 255],  #clr map
                                               [153, 153, 153, 255],  #tog grid
                                               [  3, 163,  59, 255],  #save
                                               [171,  67,  19, 255] ] #load

        self.gui_button_numbers = len(self.gui_button_labels)
        self.gui_button_padding = 10
        self.gui_button_height = self.gui_height * .65
        self.gui_button_width = (((self.gui_width - self.gui_button_padding) / 
                                   self.gui_button_numbers) - 
                                   self.gui_button_padding)
        self.gui_button_label_font_size = self.width / 140
        self.gui_button_label_font = "Arail"
        #======================================================================#

        self.gui = gui.GUI(self.gui_pos,
                           self.gui_width,
                           self.gui_height,
                           self.gui_color, 
                           self.gui_button_width,
                           self.gui_button_height,
                           self.gui_button_padding,
                           self.gui_button_colors,
                           self.gui_button_hover_colors,
                           self.gui_button_label_colors,
                           self.gui_button_label_hover_colors,
                           self.gui_button_labels,
                           self.gui_button_label_font_size,
                           self.gui_button_label_font,
                           self.gui_button_functions,
                           self.gui_button_args)

    def voronoi_setup(self):
        #Be aware that if the seed number is too large, it may take
        #a very (very) long time to solve the voronoi diagram.
        #Also note that if too many seeds exist with too high padding,
        #a diagram may fail to be created.
        self.voronoi_seeds_number = 30
        self.voronoi_seeds_padding = 100

        #To keep track attempts made during populatoin.
        self.voronoi_population_attempt = 0
        self.voronoi_population_attempts = 200 #(see populate_seed for use)

        #These are used for visualizing the voronoi border generation.
        self.voronoi_gen_borders = None
        self.voronoi_gen_borders_color = [0, 0, 0, 255]

        self.voronoi = voronoi.Voronoi(self.width,
                                       self.layer_height,
                                       self.voronoi_seeds_number, 
                                       self.voronoi_seeds_padding)
    ############################################################################

    #The following are pyglet event handlers and consist of the core logic for
    #the program. These are responsible for state changes and modifications
    #before drawing is done (on_draw is the last method in this section).
    #Also a note about on_resize: it will erase the whole map, so be careful!
    #Its main purpose is for scaling things to screen sizes, but it can be
    #disabled in app.py, and window width/height can be manually adjusted
    #in __init__
    ############################################################################
    def on_key_press(self, symbol, modifiers):
        if symbol == key.DELETE and self.cursor.type == "Select":
            self.cursor.delete_selected()
        elif symbol == key.ESCAPE:
            self.change_cursor_type(cursor.Cursor.empty_fn, None, "Default")
        elif symbol == key.S:
            self.show_generation = not self.show_generation

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor.move(dx, dy)
        self.update_cursor_img()
        self.gui.check_hovered(self.cursor.pos)
        if self.gui.hovered:
            self.cursor.toggle_visibility(True)

    def on_mouse_press(self, x, y, button, modifiers):
        #Gui is hovered, so click interacts with gui, not map.
        if self.gui.hovered:
            self.gui.clicked() #gui knows where cursor is from on_mouse_motion
        else:
            self.cursor() #call the function that cursor holds

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy) #dragged means mouse moves

        #Tell cursor that it's dragged (for use in selecet_obj).
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
        self.update_cursor_img()

    def on_mouse_enter(self, x, y): #called when mouse enters the program window
        self.cursor.move_to(x, y)   #moves cursor in case it lost track

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.setup()

    def on_draw(self):
        self.layer.draw()
        self.cursor.draw()
        self.gui.draw()
    ############################################################################

    #The following is for random map generation. It uses voronoi.py to place
    #seeds and solve a voronoi diagram for them. There are options for both
    #visualizing and not visualizing the generation
    #(visualizing looks really cool, though). See on_key_press for toggle.
    ############################################################################
    def generate_random_map(self, dt = None): 
        #dt used for clock scheduling if random map generation is toggled on

        #Sets up a voronoi diagram of seeds on first call.
        if dt == None:
            self.voronoi_setup()

        #Solves the diagram of seeds using Fortune's Algorithm (see voronoi.py).

        #For visual generation
        #----------------------------------------------------------------------#
        if self.show_generation and dt == None:
            #Call this function every clock tick to iterate to next stage in
            #voronoi solving so that its effects can still be drawn.
            #(a while/for loop pauses program --> no drawing)
            self.clock.schedule(self.generate_random_map)

        elif self.show_generation:
            points = self.voronoi.solve_visually()

            if points == None: #border generation is done
                self.clock.unschedule(self.generate_random_map)
                self.visual_populate_voronoi()

            else:
                if self.voronoi_gen_borders != None:
                    #So the past borders don't show up.
                    self.voronoi_gen_borders.delete()

                num_points = len(points) // 2
                vertices = ("v2f", points)
                vertices_colors = ("c4B", 
                                   self.voronoi_gen_borders_color * num_points)

                self.voronoi_gen_borders = self.layer.batch.add(
                                   num_points, pyglet.gl.GL_LINES, None,
                                   vertices, vertices_colors)
        #----------------------------------------------------------------------#

        #For not visual generation
        #----------------------------------------------------------------------#
        else:
            self.voronoi.solve()

            #Adds map objects to the diagram randomly.
            self.populate_voronoi()
        #----------------------------------------------------------------------#

    # The following is for the non-visual population of the voronoi diagram
    # (random map generation). It will cause the program to hang for a few
    # moments (maybe minutes, depending on seed numbers).
    #==========================================================================#
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
    #==========================================================================#

    # The following is for visualizing the generation of the random map
    # (aka the voronoi diagram and then the population).
    # Large seed numbers may take a very long time to compute (minutes/tens of)
    # but can sometimes yield better-looking maps.
    #==========================================================================#
    def visual_populate_voronoi(self, dt = None):
        if dt == None: #first run through
            #Schedule repeated calls of this function so that
            #its effects can still be drawn.
            #(a while/for loop pauses program --> no drawing)
            self.clock.schedule(self.visual_populate_voronoi)

            for seed in self.voronoi.seeds:
                #Each seed in a voronoi diagram has a polygonal shape around it.
                polygon = seed.get_polygon()
                seed.polygon = polygon

                #Choose a set of objects to fill with. (defined in obj_setup)
                seed.map_obj_set = random.choice(self.voronoi_object_sets)

        elif self.voronoi_population_attempt > self.voronoi_population_attempts:
            #Tried enough populations. Stop it.
            self.clock.unschedule(self.visual_populate_voronoi)
            self.voronoi_population_attempt = 0 #reset attempts for future runs

        else:
            for seed in self.voronoi.seeds:
                self.visual_populate_seed(seed)

            self.voronoi_population_attempt += 1

    def visual_populate_seed(self, seed):
        if self.show_generation:
            #Get a bounding rect of mins/maxs to try coordinates inside.
            (min_x, max_x, min_y, max_y) = seed.polygon.get_maxs_mins()

            obj_type = random.choice(seed.map_obj_set) #pick an object from set

            x = random.randrange(int(min_x), int(max_x) + 1) #+1 in case euqal
            y = random.randrange(int(min_y), int(max_y) + 1) #+1 in case euqal
            pos = (x, y)

            if seed.polygon.contains_point(pos):
                self.add_map_obj(pos, *obj_type) #*obj in case obj has a subtype
    #==========================================================================#
    ############################################################################

    #The following is a collection of methods called from event handlers to
    #change states of things such as the cursor's functionality,
    #map clearing, and map obj creation/addition.
    ############################################################################
    def add_map_obj(self, pos, obj_type, obj_subtype = None,
                    from_cursor = False):
        #From cursor is to know if pos is given
        #as a function that returns a pos
        #or if pos is a tuple containing (x, y)
        if from_cursor:
            pos = pos()

        obj = self.make_map_obj(pos, obj_type, obj_subtype)

        if self.layer.add_if_not_intersecting(obj): #successful placement
            obj.place(self.layer.batch)

    def make_map_obj(self, pos, obj_type, obj_subtype = None,
                     alpha = False, alpha_value = None, from_cursor = False):
        if from_cursor: #True means pos is given as a method (cursor.get_pos)
            pos = pos()

        #Colors below are copied in case the alpha value must be changed.
        #Object type is hadnled on case bases, and subtypes are handled
        #within parent types. Alpha values are handled within object types
        #since each object has differing color needs. ONE object is returned
        #at the end.
        #======================================================================#
        #The alpha value is always at index 3 --> [r, g, b, a]
        alpha_index = 3

        #Tree handling
        #----------------------------------------------------------------------#
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
        #----------------------------------------------------------------------#

        #Mountain handling
        #----------------------------------------------------------------------#
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
        #----------------------------------------------------------------------#

        #Hill handling
        #----------------------------------------------------------------------#
        elif obj_type == "Hill":
            hill_color = list(self.hill_color)

            radius = self.hill_radius * self.scale

            if alpha:
                hill_color[alpha_index] = alpha_value

            obj = map_obj.Hill(pos, radius, hill_color)
        #----------------------------------------------------------------------#

        #Lake handling
        #----------------------------------------------------------------------#
        elif obj_type == "Lake":
            lake_color = list(self.lake_water_color)

            radius = self.lake_radius * self.scale

            if alpha:
                lake_color[alpha_index] = alpha_value

            obj = map_obj.Lake(pos, radius, lake_color)
        #----------------------------------------------------------------------#

        #House handling
        #----------------------------------------------------------------------#
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

            obj = map_obj.House(pos, width, height,
                                wall_color, door_color, roof_color)
        #----------------------------------------------------------------------#
        #======================================================================#

        #One object returned always.
        return obj

    def select_obj(self, pos, from_cursor = False): #called on a mouse press
        if from_cursor:
            pos = pos() #pos is given as self.cursor.get_pos

        if self.cursor.selected == None: #cursor hasn't selected anything
            obj = self.layer.get_obj_at_pos(pos)
            self.layer.remove_obj(obj)
            obj.migrate(self.cursor.batch)
            self.cursor.selected = obj
            obj.change_visibility(self.cursor_selection_visibility)

        elif (not self.cursor.dragged and #not dragged means place the held obj
              self.layer.add_if_not_intersecting(self.cursor.selected)):
                self.cursor.selected.change_visibility(255) #255 --> full vis
                self.cursor.selected.migrate(self.layer.batch)
                self.cursor.selected = None #remove from cursor

    def clear_map(self):
        self.layer_setup() #layer setup will just re-make the layer and regions

    def update_cursor_img(self):
        if self.cursor.img != None:
            self.cursor.img.delete() #remove previous image
            self.cursor.img = None

        if self.cursor.type == "Map_obj":
            self.cursor.img = (
                   self.make_map_obj(*self.cursor.args[:-1], #ignore cursor type
                   alpha = True, alpha_value = self.cursor_selection_visibility,
                   from_cursor = True)
                              )

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

            self.cursor.toggle_visibility(True)

        elif self.cursor.type == "Map_obj":
            self.cursor.toggle_call_default(False)

            if not self.gui.hovered:
                self.cursor.toggle_visibility(False)

    def toggle_grid(self, set_to = None):
        if set_to == None:
            self.layer_grid_visibility = not self.layer_grid_visibility
        else:
            self.layer_grid_visibility = set_to

        self.layer.toggle_grid(self.layer_grid_visibility)

        if self.layer_grid_visibility and self.voronoi_gen_borders != None:
            self.voronoi_gen_borders.delete()
            self.voronoi_gen_borders = None
    ############################################################################

    #The following is for saving/loading a map file (.txt file). It uses
    #fileio.py to create a file dialog for picking a file to save/load.
    ############################################################################
    def get_save_string(self):
        save_string = str()
        seen_objs = set()
        for region in self.layer.regions:
            for obj in region.objects:
                if obj not in seen_objs:
                    string = obj.get_save_string()
                    save_string += "\n" + string
                seen_objs.add(obj)
        fileio.save_file_string(save_string)

    def load_from_string(self):
        self.clear_map()
        string = fileio.open_file_string()
        objects = list()

        #Each line looks like this:
        #Obj_type((x, y); w; h; color1; color2...; extra_args)
        #Ex: Tree((155, 28); 20; 20; [45, 112, 3, 255]; [112, 52, 3, 255]; 1)
        for line in string.splitlines():
            line = line.strip()

            if line == "" or line[0] == "#": #ignore empty lines and comments
                print(line)
                continue

            #First, get the object type (everything up to the first '(')
            for (i, c) in enumerate(line):
                if c == "(":
                    obj_type = line[:i]
                    line = line[i + 1:-1] #get rid of the obj_type and parens
                    break

            #Next, gather the args to be put into map_obj(*args)
            args = list()
            for arg in line.split(";"): #arguments all always separated by ;
                arg = arg.strip()

                if arg[0] == "(" and arg[-1] == ")": #tuple-type argument
                    arg = arg[1:-1]
                    sub_args = arg.split(",")
                    arg = tuple(map(int, sub_args))

                elif arg[0] == "[" and arg[-1] == "]": #list-type argument
                    arg = arg[1:-1]
                    sub_args = arg.split(",")
                    arg = list(map(int, sub_args))

                elif "." in arg: #float-type argument
                    if arg.replace(".", "").isdigit():
                        arg = float(arg)

                elif arg.isdigit(): #int-type argument
                    arg = int(arg)

                elif arg == "True" or arg == "False": #bool-type argument
                    arg = bool(arg)

                elif arg == "None": #None-type argument
                    arg = None

                args.append(arg)
            
            #Last, make the object with the type and arguments
            if obj_type == "Tree":
                objects.append(map_obj.Tree(*args))

            elif obj_type == "Mountain":
                objects.append(map_obj.Mountain(*args))

            elif obj_type == "House":
                objects.append(map_obj.House(*args))

            elif obj_type == "Hill":
                objects.append(map_obj.Hill(*args))
            
            elif obj_type == "Lake":
                objects.append(map_obj.Lake(*args))

        #Now add all the objects into the map
        for obj in objects:
            #Note, this uses add instead of add_if_not_intersecting
            #for a couple notable reasons:
            #1 quicker; 2 SAVED maps won't have intersections
            #BUT if the saved txt file is edited, it is a way to get
            #overlapping objects (albeit tediously)
            self.layer.add(obj)
            obj.place(self.layer.batch)
    ############################################################################

map_maker = Map_maker()
map_maker.set_caption("Map Maker")
pyglet.app.run()
