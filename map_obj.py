import math
import pyglet
from pyglet.gl import GL_LINES, GL_TRIANGLES
import shapes
import random

class Map_obj(object):
    def __init__(self, pos, width, height, parent, box_color = (252, 35, 35, 0)):
        self.pos = pos
        self.width = width
        self.height = height
        self.parent = parent
        self.box_color = list(box_color)
        self.setup()

    def setup(self):
        self.components = list()
        self.make_box()
        self.make_components()

    def make_box(self):
        self.box_shape = shapes.Rect(self.pos, self.width, self.height, (0, self.height / 2))
        self.box = Component(self.box_shape, self.box_color, GL_LINES, False)
        self.components.append(self.box)

    def place(self):
        for component in self.components:
            component.vertex_list = self.parent.batch.add(component.number_of_points, component.draw_type, None, component.vertices, component.vertices_colors)

    def delete(self):
        for component in self.components:
            component.vertex_list.delete()

    def make_components(self):
        pass

    def intersects(self, other):
        intersects = False
        if self.is_near(other):
            for component in self.components:
                if component.for_collision:
                    for other_component in other.components:
                        if other_component.for_collision and component.intersects(other_component):
                            intersects = True
        return intersects

    def is_near(self, other):
        #takes max dimension of either object and tests if their positions
        #are closer than 2x that distance (since 1x may not encompass the other)
        distance = max(self.height, other.height, self.width, other.width) * 2
        return shapes.Line.point_to_point(self.pos, other.pos) < distance

    def draw(self):
        for component in self.components:
            component.draw()

    def show_box(self, show):
        if show:
            visibility = 255
        else:
            visibility = 0
        self.box.vertex_list.colors[3::4] = [visibility] * self.box.number_of_points

    def move(self, pos):
        self.pos = pos
        for component in self.components:
            component.move(pos)

class Tree(Map_obj):
    def __init__(self, pos, width, height, parent, 
                 leaf_color, trunk_color,
                 number_of_leaves):
        self.leaf_color = leaf_color
        self.trunk_color = trunk_color
        self.number_of_leaves = number_of_leaves
        super().__init__(pos, width, height, parent)

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
            l = Component(t, self.leaf_color, GL_TRIANGLES)
            self.leaves.append(l)

    def make_trunk(self):
        trunk_height = self.height *.1
        trunk_width = self.width / 3
        x = self.pos[0]
        y = self.pos[1] + trunk_height / 2
        r = shapes.Rect((x, y), trunk_width, trunk_height)
        self.trunk = Component(r, self.trunk_color, GL_TRIANGLES)

class Mountain(Map_obj):
    def __init__(self, pos, width, height, parent,
                 rock_color, has_snow, snow_color = None):
        self.rock_color = rock_color
        self.has_snow = has_snow
        self.snow_color = snow_color
        super().__init__(pos, width, height, parent)

    def make_components(self):
        self.make_rock()
        self.components.append(self.rock)
        if self.has_snow:
            self.make_snow()
            self.components.append(self.snow)

    def make_rock(self):
        offset = (0, self.height / 2)
        t = shapes.Iso_triangle(self.pos, self.width, self.height, offset)
        self.rock = Component(t, self.rock_color, GL_TRIANGLES)

    def make_snow(self):
        snow_height = self.height / 3
        snow_width = self.width / 3
        offset = (0, self.height / 2 + snow_height)
        t = shapes.Iso_triangle(self.pos, snow_width, snow_height, offset)
        self.snow = Component(t, self.snow_color, GL_TRIANGLES, False)

class Hill(Map_obj):
    def __init__(self, pos, width, height, parent, hill_color):
        self.hill_color = hill_color
        super().__init__(pos, width, height, parent)

    def make_components(self):
        shape = shapes.Circle(self.pos, self.height, 5, angle = math.pi)
        c = Component(shape, self.hill_color, GL_TRIANGLES)
        self.components.append(c)

class Lake(Map_obj):
    def __init__(self, pos, width, height, parent, water_color):
        self.water_color = water_color
        super().__init__(pos, width, height, parent)

    def make_components(self):
        angles = [0, 45, 90, 100, 180, 270, 300]
        widths = [20] * len(angles)
        shape = shapes.Simple_polygon(self.pos, angles, widths, radians = False)
        component = Component(shape, self.water_color, GL_TRIANGLES)
        self.components.append(component)

class House(Map_obj):
    def __init__(self, pos, width, height, parent,
                 wall_color, door_color, roof_color):
        self.wall_color = wall_color
        self.door_color = door_color
        self.roof_color = roof_color
        super().__init__(pos, width, height, parent)
    
    def make_components(self):
        self.make_walls()
        self.make_roof()
        self.make_door()

    def make_walls(self):
        height = self.height * .6
        width = self.width * .75
        offset = (0, height / 2)
        rect = shapes.Rect(self.pos, width, height, offset)
        wall = Component(rect, self.wall_color, GL_TRIANGLES)
        self.components.append(wall)

    def make_door(self):
        height = self.height * .4
        width = self.width * .2
        offset = (0, height / 2)
        rect = shapes.Rect(self.pos, width, height, offset)
        door = Component(rect, self.door_color, GL_TRIANGLES, False)
        self.components.append(door)
    
    def make_roof(self):
        height = self.height * .4
        offset = (0, self.height - height / 2)
        tri = shapes.Iso_triangle(self.pos, self.width, height, offset)
        roof = Component(tri, self.roof_color, GL_TRIANGLES)
        self.components.append(roof)

class Component(object):
    def __init__(self, shape, color, draw_type, for_collision = True):
        self.shape = shape
        self.color = color
        self.batch_vertex_list = None
        self.draw_type = draw_type
        self.for_collision = for_collision
        if self.draw_type == GL_TRIANGLES:
            self.number_of_points = len(self.shape.triangular_points) // 2
            self.vertices = ("v2f", self.shape.triangular_points)
            self.vertices_colors = (f"c{len(self.color)}B",
                                    self.color * self.number_of_points)
        elif self.draw_type == GL_LINES:
            self.number_of_points = len(self.shape.lines_points) // 2
            self.vertices = ("v2f", self.shape.lines_points)
            self.vertices_colors = (f"c{len(self.color)}B",
                                    self.color * self.number_of_points)

        self.vertex_list = pyglet.graphics.vertex_list(self.number_of_points,
                                                       self.vertices,
                                                       self.vertices_colors)

    def intersects(self, other):
        if self.shape.intersects(other.shape):
            return True
        else:
            return False

    def move(self, pos):
        self.shape.move(pos)
        if self.draw_type == GL_TRIANGLES:
            self.vertex_list.vertices[:] = self.shape.triangular_points
        else:
            self.vertex_list.vertices[:] = self.shape.lines_points

    def draw(self):
        self.vertex_list.draw(self.draw_type)