################################################################################
#
#   vector.py
#   Code by: Casey Walker
#
################################################################################

import math
import line

class Vector(object):
    def __init__(self, pos, direction):
        self.beginning_point = pos
        self.direction = direction
        self.angle = math.atan2(direction[1], direction[0])
        self.terminating_point = (self.beginning_point[0] + self.direction[0], 
                                  self.beginning_point[1] + self.direction[1])
        self.magnitude = (self.direction[0] ** 2 + self.direction[1] ** 2) ** (1/2)
        self.line = line.Line(pos, line.Line.find_slope(self.beginning_point, self.terminating_point))

    def __repr__(self):
        return f"Vector {self.direction} at {self.beginning_point}"

    @staticmethod
    def get_unit_vector(vector):
        if math.isclose(vector.magnitude, 1): #already a unit vector
            return vector
        else:
            unit_direction = (vector.direction[0] / vector.magnitude, vector.direction[1] / vector.magnitude)
            return Vector((0, 0), unit_direction) #center unit vectors at the origin

    def angle_to(self, vector, counter_clockwise = True): #calculates the angle to vector going counter-clockwise (unless specified otherwise)
        angle = vector.angle - self.angle
        if counter_clockwise and angle < 0:
            angle = math.pi * 2 + angle
        elif not counter_clockwise and angle < 0:
            angle = abs(angle)
        elif not counter_clockwise:
            angle = math.pi * 2 - angle
        return angle

    def point_in_domain_and_range(self, point):
        (x, y) = point
        (x0, y0) = self.beginning_point
        (x1, y1) = self.terminating_point
        if (min(x0, x1) <= x <= max(x0, x1) and
           min(y0, y1) <= y <= max(y0, y1)):
           return True
        elif ((math.isclose(x0, x, abs_tol = 1e-7) and math.isclose(y0, y, abs_tol = 1e-7)) or 
            (math.isclose(x1, x, abs_tol = 1e-7) and math.isclose(y1, y, abs_tol = 1e-7))):
            return True
        else:
            return False

    def contains_point(self, point):
        if self.line.contains_point(point) and self.point_in_domain_and_range(point):
            return True
        else:
            return False
    
    def intersection(self, line):
        if self.line.intersects(line):
            intersection = self.line.intersection(line)
            if self.point_in_domain_and_range(intersection):
                return intersection
        return None
