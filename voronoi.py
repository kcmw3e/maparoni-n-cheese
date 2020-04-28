################################################################################
#
#   voronoi.py
#   Code by: Casey Walker
#
################################################################################
 
import shapes
import pyglet
import random
import math

class Voronoi(object):
    def __init__(self, width, height, number_of_seeds, seed_padding):
        self.width = width
        self.height = height
        self.number_of_seeds = number_of_seeds
        self.seed_padding = seed_padding
        self.sweepline_height = 0
        self.sweepline_step = 1
        self.sweepline = shapes.Line((0, self.sweepline_height), 0)
        if self.generate_seed_points():
            self.generate_seeds()
        else:
            print("ERROR")
        self.generate_borderlines()

    def generate_seed_points(self):
        points = list()
        max_iterations = 1000
        iterations = 0
        while len(points) < self.number_of_seeds and iterations < max_iterations:
            iterations += 1
            x = random.randrange(self.seed_padding, (self.width - self.seed_padding))
            y = random.randrange(self.seed_padding, (self.height - self.seed_padding))
            point = (x, y)
            point_invalid = False
            for other_point in points:
                if isnear(point, other_point, self.seed_padding):
                        point_invalid = True
            if not point_invalid:
                points.append(point)
        if iterations >= max_iterations:
            success = self.generate_seed_points()
            if not success:
                return False
        self.points = points
        return True

    def generate_seeds(self):
        self.seeds = list()
        for point in self.points:
            self.seeds.append(Voronoi_seed(point, self))

    def generate_borderlines(self):
        self.borderlines = dict()
        left = shapes.Line((0, 0), None)
        right = shapes.Line((self.width, 0), None)
        top = shapes.Line((0, self.height), 0)
        bottom = shapes.Line((0, 0), 0)
        self.borderlines["left"] = left
        self.borderlines["right"] = right
        self.borderlines["top"] = top
        self.borderlines["bottom"] = bottom

    def solve(self):
        while self.sweepline_height < self.height * 1.75:
            self.move_sweepline(self.sweepline_step)

    def solve_visually(self):
        if self.sweepline_height > self.height * 1.75:
            return None
        else:
            self.move_sweepline(self.sweepline_step)
            seed_points = list()
            for seed in self.seeds:
                if seed.active:
                    points = seed.poll_flattened_points()
                    seed_points.extend(points)
            return seed_points

    def move_sweepline(self, dy):
        self.sweepline_height += dy
        self.sweepline.y = self.sweepline_height
        self.test_seeds()

    def test_seeds(self):
        for seed in self.seeds:
            if not seed.active and self.sweepline > seed.pos:
                seed.activate(self.sweepline_height, 0, self.width, 0, self.height, self.borderlines)
            elif not seed.complete and seed.active:
                seed.adjust(self.sweepline_height, self.seeds, self.borderlines)

    def intersection_in_bounds(self, intersection):
        return (self.borderlines["left"  ] < intersection and
                self.borderlines["right" ] > intersection and
                self.borderlines["top"   ] > intersection and
                self.borderlines["bottom"] < intersection)

    def intersection_is_edge(self, intersection):
        valid = True
        for seed in self.seeds:
            if seed.active and seed.parabola > intersection:
                valid = False
        return valid

    def valid_intersection(self, intersection):
        return (self.intersection_in_bounds(intersection) and
                self.intersection_is_edge(intersection))

class Voronoi_seed(object):
    def __init__(self, pos, parent):
        self.pos = pos
        self.parent = parent
        self.active = False
        self.complete = False
        self.parabola = None
        self.intersections = dict()
        self.border_intersections = dict()

    def __lt__(self, sweepline):
        return self.pos[1] < sweepline.point[1]

    def activate(self, sweepline, x_min, x_max, y_min, y_max, borderlines):
        self.active = True
        self.parabola = shapes.Parabola(sweepline, self.pos)
        self.parabola.open_domain(x_min, x_max)
        self.parabola.open_range(y_min, y_max)
        for border in borderlines:
            line = borderlines[border]
            self.intersections[line] = [None, None]

    def adjust(self, sweepline, other_seeds, borderlines):
        self.parabola.directrix = sweepline
        for border in borderlines:
                line = borderlines[border]
                intersections = self.parabola.intersections(line)
                for (i, intersection) in enumerate(intersections):
                    if self.parent.valid_intersection(intersection):
                        self.intersections[line][i] = intersection
        for seed in other_seeds:
            if seed.active and seed != self:
                intersections = self.parabola.intersections(seed.parabola)
                if seed not in self.intersections:
                    self.intersections[seed] = [None, None]
                for (i, intersection) in enumerate(intersections):
                    if self.parent.valid_intersection(intersection):
                        self.intersections[seed][i] = intersection

    def poll_points(self):
        points = list()
        for seed in self.intersections:
            for intersection in self.intersections[seed]:
                if intersection != None:
                    points.append(intersection)
        if len(points) == 0:
            return []
        else:
            points = ordered(self.pos, points)
            return points
    
    def poll_flattened_points(self):
        points = self.poll_points()
        if len(points) == 0:
            return [ ]
        else:
            (x1, y1) = points[0]
            ordered_flattened_points = [x1, y1]
            for point in points[1:]:
                (x, y) = point
                ordered_flattened_points.extend([x, y] * 2)
            ordered_flattened_points.extend([x1, y1])
            return ordered_flattened_points

    def get_polygon(self):
        angles = list()
        widths = list()
        points = self.poll_points()
        (x1, y1) = self.pos
        for (x2, y2) in points:
            dx = x2 - x1
            dy = y2 - y1
            v = shapes.Vector(self.pos, (dx, dy))
            angle = v.angle
            width = v.magnitude
            angles.append(angle)
            widths.append(width)
        polygon = shapes.Simple_polygon(self.pos, angles, widths)
        return polygon

def isnear(point1, point2, nearness):
    return shapes.Line.point_to_point(point1, point2) < nearness

def ordered(pos, points):
    ordered_points_dict = dict()
    angles = list()
    (x1, y1) = pos
    for point in points:
        (x2, y2) = point
        dx = x2 - x1
        dy = y2 - y1
        v = shapes.Vector(pos, (dx, dy))
        angle = v.angle
        ordered_points_dict[angle] = point
        angles.append(angle)
    ordered_points = list()
    for angle in sorted(angles):
        ordered_points.append(ordered_points_dict[angle])
    return ordered_points
