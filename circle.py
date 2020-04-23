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
    def __init__(self, pos, radius, resolution = 50, offset =(0, 0), radians = True, rotation = 0, angle = 2 * math.pi):
        self.pos = pos
        self.radius = radius
        self.resolution = resolution
        self.offset = offset
        self.radians = radians
        self.rotation = rotation
        self.angle = angle
        self.generate_angles()
        self.generate_widths()
        super().__init__(self.pos, self.angles, self.widths, radians, rotation)

    def generate_angles(self):
        self.angles = list()
        dangle = self.angle / self.resolution
        angle = 0
        for i in range(self.resolution):
            angle = dangle * i
            self.angles.append(angle)
    
    def generate_widths(self):
        self.widths = [self.radius] * self.resolution
