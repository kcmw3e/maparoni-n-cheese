################################################################################
#
#   triangle.py
#   Code by: Casey Walker
#
################################################################################

import math
import line
import polygon

class Iso_triangle(polygon.Simple_polygon):
    #pos is the center of rotation, if left (0, 0) rotation is about center of the triangle
    #rotation describes the angle to rotate the triangle by on initialization (if left zero --> triangle's base is horizontal)
    #offset is the distance from pos to the symmetry axis and base of the triangle (as a tuple, (dx, dy))
    def __init__(self, pos, base, height, offset = (0, 0), radians = True, rotation = 0):
        self.pos = pos
        self.base = base
        self.height = height
        self.offset = offset
        self.radians = radians
        self.rotation = rotation if radians else math.radians(rotation)
        self.generate_angles()
        self.generate_widths()
        super().__init__(self.pos, self.angles, self.widths, self.radians, self.rotation)

    def generate_angles(self):
        self.angles = list()
        dx = self.offset[0] + self.base / 2
        dy = self.offset[1] - self.height / 2
        angle0 = math.atan2(dy, dx)
        dx = self.offset[0]
        dy = self.offset[1] + self.height / 2
        angle1 = math.atan2(dy, dx)
        dx = self.offset[0] - self.base / 2
        dy = self.offset[1] - self.height / 2
        angle2 = math.atan2(dy, dx)
        self.angles.extend([angle0, angle1, angle2])

    def generate_widths(self):
        self.widths = list()
        dx = self.offset[0] + self.base / 2 + self.pos[0]
        dy = self.offset[1] - self.height / 2 + self.pos[1]
        point = (dx, dy)
        self.widths.append(line.Line.point_to_point(self.pos, point))
        dx = self.offset[0] + self.pos[0]
        dy = self.offset[1] + self.height / 2 + self.pos[1]
        point = (dx, dy)
        self.widths.append(line.Line.point_to_point(self.pos, point))
        dx = self.offset[0] - self.base / 2 + self.pos[0]
        dy = self.offset[1] - self.height / 2 + self.pos[1]
        point = (dx, dy)
        self.widths.append(line.Line.point_to_point(self.pos, point))


        