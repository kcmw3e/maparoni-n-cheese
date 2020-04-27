import math
import pyglet
from pyglet.gl import GL_LINES, GL_TRIANGLES
import shapes
import random

class Map_obj(object):
    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.setup()

    def setup(self):
        self.components = list()
        self.make_components()

    def place(self, parent_batch):
        self.parent_batch = parent_batch
        points = list()
        colors = list()
        for component in self.components:
            component_points = component.shape.triangular_points
            num_points = len(component_points) // 2
            component_colors = component.color * num_points
            points.extend(component_points)
            colors.extend(component_colors)
        num_points = len(points) // 2
        self.vertex_list = self.parent_batch.add(num_points, GL_TRIANGLES, None, ("v2f", points), ("c4B", colors))

    def delete(self):
        self.vertex_list.delete()

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

    def change_visibility(self, visibility):
        for i in range(3, len(self.vertex_list.colors), 4):
            self.vertex_list.colors[i] = visibility

    def move(self, dx, dy):
        (x, y) = self.pos
        self.pos = (x + dx, y + dy)
        for i in range(len(self.vertex_list.vertices)):
            if i % 2 == 0:
                self.vertex_list.vertices[i] += dx
            else:
                self.vertex_list.vertices[i] += dy
        for component in self.components:
            component.move(dx, dy)

    def scale(self, dsize):
        for component in self.components:
            component.scale(dsize)
        points = list()
        for component in self.components:
            component_points = component.shape.triangular_points
            points.extend(component_points)
        self.vertex_list.vertices = points

    def migrate(self, parent_batch):
        old_parent_batch = self.parent_batch
        self.parent_batch = parent_batch
        old_parent_batch.migrate(self.vertex_list, GL_TRIANGLES, None, self.parent_batch)

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
            l = Component(t, self.leaf_color)
            self.leaves.append(l)

    def make_trunk(self):
        trunk_height = self.height *.1
        trunk_width = self.width / 3
        x = self.pos[0]
        y = self.pos[1] + trunk_height / 2
        r = shapes.Rect((x, y), trunk_width, trunk_height)
        self.trunk = Component(r, self.trunk_color)

class Mountain(Map_obj):
    def __init__(self, pos, width, height,
                 rock_color, has_snow, snow_color = None):
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
        self.rock = Component(t, self.rock_color)

    def make_snow(self):
        snow_height = self.height / 3
        snow_width = self.width / 3
        offset = (0, self.height / 2 + snow_height)
        t = shapes.Iso_triangle(self.pos, snow_width, snow_height, offset)
        self.snow = Component(t, self.snow_color, False)

class Hill(Map_obj):
    def __init__(self, pos, width, height, hill_color):
        self.hill_color = hill_color
        super().__init__(pos, width, height)

    def make_components(self):
        shape = shapes.Circle(self.pos, self.height, 5, angle = math.pi)
        c = Component(shape, self.hill_color)
        self.components.append(c)

class Lake(Map_obj):
    def __init__(self, pos, width, height, water_color):
        self.water_color = water_color
        super().__init__(pos, width, height)

    def make_components(self):
        angles = [0, 45, 90, 100, 180, 270, 300]
        widths = [20] * len(angles)
        shape = shapes.Simple_polygon(self.pos, angles, widths, radians = False)
        component = Component(shape, self.water_color)
        self.components.append(component)

class House(Map_obj):
    def __init__(self, pos, width, height,
                 wall_color, door_color, roof_color):
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
        wall = Component(rect, self.wall_color)
        self.components.append(wall)

    def make_door(self):
        height = self.height * .4
        width = self.width * .2
        offset = (0, height / 2)
        rect = shapes.Rect(self.pos, width, height, offset)
        door = Component(rect, self.door_color, False)
        self.components.append(door)

    def make_roof(self):
        height = self.height * .4
        offset = (0, self.height - height / 2)
        tri = shapes.Iso_triangle(self.pos, self.width, height, offset)
        roof = Component(tri, self.roof_color)
        self.components.append(roof)

class Component(object):
    def __init__(self, shape, color, for_collision = True):
        self.shape = shape
        self.color = color
        self.for_collision = for_collision

    def intersects(self, other):
        if self.shape.intersects(other.shape):
            return True
        else:
            return False

    def move(self, dx, dy):
        self.shape.move(dx, dy)

    def scale(self, dsize):
        self.shape.scale(dsize)