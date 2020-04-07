################################################################################
#
#   circle.py
#   Code by: Casey Walker
#
################################################################################

import math
import pyglet
import polygon

class Circle(polygon.Simple_polygon):
    def __init__(self, pos, radius, resolution = 50, offset =(0, 0), radians = True, rotation = 0):
        self.pos = pos
        self.radius = radius
        self.resolution = resolution
        self.offset = offset
        self.radians = radians
        self.rotation = rotation
        self.generate_angles()
        self.generate_widths()
        super().__init__(self.pos, self.angles, self.widths, radians)

    def generate_angles(self):
        self.angles = list()
        dangle = math.pi * 2 / self.resolution
        angle = 0
        for i in range(self.resolution):
            angle = dangle * i
            self.angles.append(angle)
    
    def generate_widths(self):
        self.widths = [self.radius] * self.resolution
