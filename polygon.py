################################################################################
#
#   polygon.py
#   Code by: Casey Walker
#
################################################################################

import math
import vector
import line

# Note about Simple_polygon class:
#   Points should be defined by angles in order going counter-clockwise around 
#   the center of rotation (pos). Widths define the distance to each point from
#   pos. Angles and widths are co-indexed, so angles[i] corresponds to widths[i]
#   
#   If collision detection is an intended use with this, some guidelines
#   should be followed:
#       1) Angles should remain under 180 degrees between each other 
#          (i.e the angle between 2 vectors at a point should not exceed 180
#           degrees with respect to the main body of the polygon)
#       2) The polygon should not "double" back on itself or overlap itself
class Simple_polygon(object):
    def __init__(self, pos, angles, widths, radians = True, rotation = 0):
        self.pos = pos #pos defines the center of rotation of the polygon
        self.radians = radians
        self.angles = tuple(angles) #contains the angles to generate points
        self.widths = tuple(widths) #contains the distances to each point
        self.radians = radians
        self.rotation = rotation
        self.setup()
    
    def setup(self):
        self.generate_points()
        self.generate_trianglular_points()
        self.generate_lines_points()
        self.generate_perimeter_vectors()
        self.rotate(self.rotation)

    def generate_points(self):
        self.points = list()
        self.flattened_points = list()
        for i in range(len(self.angles)):
            angle = self.angles[i]
            if not self.radians:
                angle = math.radians(angle)
            dx = math.cos(angle) * self.widths[i]
            dy = math.sin(angle) * self.widths[i]
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            point = (x, y)
            self.points.append(point)
            self.flattened_points.extend([x, y])

    def generate_trianglular_points(self): #for drawing the shape in triangles
        self.triangular_points = list()
        (x0, y0) = self.points[0]
        for i in range(1, len(self.points) - 1):
            (x1, y1) = self.points[i]
            (x2, y2) = self.points[i + 1]
            self.triangular_points.extend([x0, y0, x1, y1, x2, y2])

    def generate_lines_points(self): #for drawing the shape in line loops
        self.lines_points = list()
        for i in range(len(self.points)):
            j = i - 1
            (x1, y1) = self.points[i]
            (x2, y2) = self.points[j]
            self.lines_points.extend([x1, y1, x2, y2])

    #generate the vectors from point to point around the perimeter
    def generate_perimeter_vectors(self):
        vectors = list()
        for i in range(len(self.points)):
            j = i + 1
            if j == len(self.points): #at last point
                j = 0 #close the loop with the first point
            point1 = self.points[i]
            point2 = self.points[j]
            dx = point2[0] - point1[0]
            dy = point2[1] - point1[1]
            direction = (dx, dy)
            vectors += [vector.Vector(point1, direction)]
        self.vectors = tuple(vectors)

    def scale(self, dwidth):
        dwidth = 2 ** dwidth
        widths = list()
        for width in self.widths:
            width *= dwidth
            widths.append(width)
        self.widths = tuple(widths)
        self.setup()

    def intersects(self, other):
        for point in other.points:
            if self.contains_point(point):
                return True
        for point in self.points:
            if other.contains_point(point):
                return True
        return False

    def contains_point(self, point):
        for i in range(len(self.vectors)):
            j = i - 1
            v = self.vectors[i]
            direction_to_point = (point[0] - v.beginning_point[0],
                                  point[1] - v.beginning_point[1])
            vector_to_point = vector.Vector(v.beginning_point,
                                            direction_to_point)
            previous_vector = self.vectors[j] #negative index when i = 0
            angle = v.angle_to(vector_to_point)
            angle_to_previous = v.angle_to(previous_vector)
            if angle > angle_to_previous:
                return False
            elif angle == angle_to_previous and not v.contains_point(point):
                return False
        return True

    def intersections(self, other):
        intersections = list()
        if isinstance(other, Simple_polygon):
            for vector in self.vectors:
                for other_vector in other.vectors:
                    if vector.intersects(other_vector):
                        intersection = vector.intersection(other_vector)
                        intersections.append(intersection)
        elif isinstance(other, line.Line):
            for vector in self.vectors:
                intersection = vector.intersection(line)
                if intersection != None:
                    intersections.append(intersection)
        return intersections

    def rotate(self, dangle):
        rotated_angles = list()
        for angle in self.angles:
            rotated_angles.append(angle+dangle)
        self.angles = tuple(rotated_angles)
        self.generate_points()
        self.generate_trianglular_points()
        self.generate_lines_points()
        self.generate_perimeter_vectors()
    
    def move(self, dx, dy):
        (x, y) = self.pos
        self.pos = (x + dx, y + dy)
        self.setup()

    def get_maxs_mins(self):
        max_x = max_y = None
        min_x = min_y = None
        for point in self.points:
            (x, y) = point
            if max_x == None or x > max_x:
                max_x = x
            if min_x == None or x < min_x:
                min_x = x
            if max_y == None or y > max_y:
                max_y = y
            if min_y == None or y < min_y:
                min_y = y
        return (min_x, max_x, min_y, max_y)