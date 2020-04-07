################################################################################
#
#   line.py
#   Code by: Casey Walker
#
################################################################################

import math

class Line(object):
    def __init__(self, point, slope):
        self.point = point
        (self.x, self.y) = self.point
        self.slope = slope

    def __gt__(self, point):
        (x, y) = point
        if y < self.output(x):
            return True
        else:
            return False
        
    def __lt__(self, point):
        (x, y) = point
        if self.output(x) < y:
            return True
        else:
            return False
    
    def __repr__(self):
        return f"y = {self.slope} * (x - {self.x}) + {self.y}"

    @staticmethod
    def point_to_point(point1, point2):
        (x1, y1) = point1
        (x2, y2) = point2
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1/2)

    @staticmethod
    def find_slope(point1, point2):
        (x1, y1) = point1
        (x2, y2) = point2
        dy = (y1 - y2)
        dx = (x1 - x2)
        if dx == 0:
            return None
        else:
            return dy / dx

    def contains_point(self, point):
        (x, y) = point
        if self.slope == None:
            if self.x == point[0]:
                return True
            else:
                return False
        else:
            if math.isclose(self.output(x), y, abs_tol = 1e-7):
                return True
            else:
                return False

    def intersects(self, line): #does not consider the same line as intersecting
        if line.slope == self.slope:
            return False
        else:
            return True

    def intersection(self, line):
        if self.intersects(line):
            #solve: self.slope * (x - self.x) + self.y = line.slope * (x - line.x) + line.y
            x =  (-line.slope*line.x + line.y + self.slope*self.x - self.y) / (self.slope - line.slope)
            y = self.output(x)
            point = (x, y)
            return point
        else:
            return None

    def output(self, x):
        if self.slope == None:
            return x
        return self.slope * (x - self.x) + self.y
