import math
import pyglet
import shapes
import random

class Map_obj(object):
    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.components = list()
        self.make_components()

    def make_components(self):
        pass

    def intersects(self, other):
        if self.is_near(other):
            for component in self.components:
                for other_component in other.components:
                    if component.intersects(other_component):
                        return True
        return False

    def is_near(self, other):
        #takes max dimension of either object and tests if their positions
        #are closer than 2x that distance (since 1x may not encompass the other)
        distance = max(self.height, other.height, self.width, other.width) * 2
        return shapes.Line.point_to_point(self.pos, other.pos) < distance

    def draw(self):
        for component in self.components:
            component.vertex_list.draw(component.draw_type)

class Tree(Map_obj):
    def __init__(self, pos, width, height, 
                 leaf_color, trunk_color,
                 number_of_leaves):
        self.leaf_color = leaf_color
        self.trunk_color = trunk_color
        self.number_of_leaves = number_of_leaves
        super().__init__(pos, width, height)

    def make_components(self):
        self.make_leaves()
        self.components.extend(self.leaves)
        self.make_trunk()
        self.components.append(self.trunk)

    def make_leaves(self):
        self.leaves = list()
        leaf_height = self.height*.9
        for i in range(self.number_of_leaves):
            leaf_height = leaf_height * (1 - .1 * i)
            offset = (0, self.height - leaf_height / 2)
            t = shapes.Iso_triangle(self.pos, self.width, leaf_height, offset)
            l = Component(t, self.leaf_color, pyglet.gl.GL_POLYGON)
            self.leaves.append(l)

    def make_trunk(self):
        trunk_height = self.height *.1
        trunk_width = self.width / 3
        x = self.pos[0]
        y = self.pos[1] + trunk_height / 2
        r = shapes.Rect((x, y), trunk_width, trunk_height)
        self.trunk = Component(r, self.trunk_color, pyglet.gl.GL_POLYGON)

class Mountain(Map_obj):
    def __init__(self, pos, width, height, rock_color, has_snow, snow_color = None):
        self.rock_color = rock_color
        self.has_snow = has_snow
        self.snow_color = snow_color
        super().__init__(pos, width, height)

    def make_components(self):
        self.make_rock()
        self.components.append(self.rock)
        if self.has_snow:
            self.make_snow()
            self.components.append(self.snow)

    def make_rock(self):
        offset = (0, self.height / 2)
        t = shapes.Iso_triangle(self.pos, self.width, self.height, offset)
        self.rock = Component(t, self.rock_color, pyglet.gl.GL_POLYGON)

    def make_snow(self):
        snow_height = self.height / 3
        snow_width = self.width / 3
        offset = (0, self.height / 2 + snow_height)
        t = shapes.Iso_triangle(self.pos, snow_width, snow_height, offset)
        self.snow = Component(t, self.snow_color, pyglet.gl.GL_POLYGON)

class Hill(Map_obj):
    def __init__(self, pos, width, height, hill_color):
        self.hill_color = hill_color
        super().__init__(pos, width, height)

    def make_components(self):
        shape = shapes.Circle(self.pos, self.height, 5, angle = math.pi)
        c = Component(shape, self.hill_color, pyglet.gl.GL_POLYGON)
        self.components.append(c)

class Lake(Map_obj):
    def __init__(self, pos, width, height, water_color):
        self.water_color = water_color
        super().__init__(pos, width, height)

    def make_components(self):
        angles = [0, 45, 90, 100, 180, 270, 300]
        widths = [20] * len(angles)
        shape = shapes.Simple_polygon(self.pos, angles, widths, radians = False)
        component = Component(shape, self.water_color, pyglet.gl.GL_POLYGON)
        self.components.append(component)

class House(Map_obj):
    def __init__(self, pos, width, height, wall_color, door_color, roof_color):
        self.wall_color = wall_color
        self.door_color = door_color
        self.roof_color = roof_color
        super().__init__(pos, width, height)
    
    def make_components(self):
        self.make_walls()
        self.make_roof()
        self.make_door()

    def make_walls(self):
        height = self.height * .6
        width = self.width * .75
        offset = (0, height / 2)
        rect = shapes.Rect(self.pos, width, height, offset)
        wall = Component(rect, self.wall_color, pyglet.gl.GL_POLYGON)
        self.components.append(wall)

    def make_door(self):
        height = self.height * .4
        width = self.width * .2
        offset = (0, height / 2)
        rect = shapes.Rect(self.pos, width, height, offset)
        door = Component(rect, self.door_color, pyglet.gl.GL_POLYGON)
        self.components.append(door)
    
    def make_roof(self):
        height = self.height * .4
        offset = (0, self.height - height / 2)
        tri = shapes.Iso_triangle(self.pos, self.width, height, offset)
        roof = Component(tri, self.roof_color, pyglet.gl.GL_POLYGON)
        self.components.append(roof)

class Component(object):
    def __init__(self, shape, color, draw_type):
        self.shape = shape
        self.color = color
        self.number_of_points = len(self.shape.triangular_points) // 2
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B",
                                self.color * self.number_of_points)
        
        self.draw_type = draw_type

        self.vertex_list = pyglet.graphics.vertex_list(self.number_of_points,
                                                       self.vertices,
                                                       self.vertices_colors)

    def intersects(self, other):
        if self.shape.intersects(other.shape):
            return True
        else:
            return False
    
    def draw(self):
        self.vertex_list.draw(self.draw_type)