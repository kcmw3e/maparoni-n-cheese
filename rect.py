################################################################################
#
#   rect.py
#   Code by: Casey Walker
#
################################################################################

import polygon
import math
import line

class Rect(polygon.Simple_polygon):
    #pos is the center of rotation, if left (0, 0) rotation is about upper-left corner
    #offset is the offset from pos (dx, dy)
    def __init__(self, pos, width, height, offset = (0, 0), radians = True, rotation = 0):
        self.pos = pos
        self.width = width
        self.height = height
        self.offset = offset
        self.radians = radians
        self.rotation = rotation
        self.generate_angles()
        self.generate_widths()
        super().__init__(self.pos, self.angles, self.widths, self.radians)

    def generate_angles(self):
        self.angles = list()
        dx = self.offset[0] + self.width / 2
        dy = self.offset[1] + self.height / 2
        angle0 = math.atan2(dy, dx)
        dx = self.offset[0] - self.width / 2
        dy = self.offset[1] + self.height / 2
        angle1 = math.atan2(dy, dx)
        dx = self.offset[0] - self.width / 2
        dy = self.offset[1] - self.height / 2
        angle2 = math.atan2(dy, dx)
        dx = self.offset[0] + self.width / 2
        dy = self.offset[1] - self.height / 2
        angle3 = math.atan2(dy, dx)
        self.angles.extend([angle0, angle1, angle2, angle3])

    def generate_widths(self):
        self.widths = list()
        dx = self.offset[0] + self.width / 2 + self.pos[0]
        dy = self.offset[1] + self.height / 2 + self.pos[1]
        pos = (dx, dy)
        width0 = line.Line.point_to_point(self.pos, pos)
        dx = self.offset[0] - self.width / 2 + self.pos[0]
        dy = self.offset[1] + self.height / 2 + self.pos[1]
        pos = (dx, dy)
        width1 = line.Line.point_to_point(self.pos, pos)
        dx = self.offset[0] - self.width / 2 + self.pos[0]
        dy = self.offset[1] - self.height / 2 + self.pos[1]
        pos = (dx, dy)
        width2 = line.Line.point_to_point(self.pos, pos)
        dx = self.offset[0] + self.width / 2 + self.pos[0]
        dy = self.offset[1] - self.height / 2 + self.pos[1]
        pos = (dx, dy)
        width3 = line.Line.point_to_point(self.pos, pos)
        self.widths.extend([width0, width1, width2, width3])
