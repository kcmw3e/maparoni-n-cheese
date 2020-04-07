################################################################################
#
#   mountain.py
#   Code by: Casey Walker
#
################################################################################

import shapes
import pyglet
import random
import math
import component

class Mountain(object):
    def __init__(self, pos, width, height, rock_color, has_snow, snow_color = None):
        self.pos = pos
        self.width = width
        self.height = height
        self.rock_color = rock_color
        self.has_snow = has_snow
        self.snow_color = snow_color
        self.components = list()
        self.make_rock()
        self.components.append(self.rock)
        if self.has_snow:
            self.make_snow()
            self.components.append(self.snow)

    def make_rock(self):
        offset = (0, self.height / 2)
        t = shapes.Iso_triangle(self.pos, self.width, self.height, offset)
        self.rock = component.Component(t, self.rock_color, pyglet.gl.GL_POLYGON)

    def make_snow(self):
        snow_height = self.height / 3
        snow_width = self.width / 3
        offset = (0, self.height / 2 + snow_height)
        t = shapes.Iso_triangle(self.pos, snow_width, snow_height, offset)
        self.snow = component.Component(t, self.snow_color, pyglet.gl.GL_POLYGON)

    def intersects(self, other):
        for component in self.components:
            for other_component in other.components:
                if component.intersects(other_component):
                    return True
        return False

    def draw(self):
        for component in self.components:
            component.vertex_list.draw(component.draw_type)



l = shapes.Line((0, 1), 0)
p = shapes.Simple_polygon((0, 0), [0, math.pi / 2, math.pi], [5, 10, 5])
print(p.intersection(l))