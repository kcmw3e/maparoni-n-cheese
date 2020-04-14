################################################################################
#
#   component.py
#   Code by: Casey Walker
#
################################################################################

import pyglet
import shapes

class Component(object):
    def __init__(self, shape, color, draw_type):
        self.shape = shape
        self.color = color
        self.number_of_points = len(self.shape.triangular_points) // 2
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B", self.color * self.number_of_points)
        self.draw_type = draw_type
        self.vertex_list = pyglet.graphics.vertex_list(self.number_of_points, self.vertices, self.vertices_colors)


    def intersects(self, other):
        if self.shape.intersects(other.shape):
            return True
        else:
            return False