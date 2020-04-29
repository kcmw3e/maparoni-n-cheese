################################################################################
#
#   voronoi.py
#   Code by: Casey Walker
#
################################################################################

import math
import random

import pyglet

import shapes

#Some notes:
#   1) The algorith used to produce the voronoi diagram in this program is
#      called Fortune's Algorithm. Descriptions can be found
#         here:
#           -- https://en.wikipedia.org/wiki/Fortune%27s_algorithm
#           -- http://blog.ivank.net/fortunes-algorithm-and-implementation.html
#      I suggest you read one or both of those (or at least skim) before you
#      try to understand the implementation below. Or you can watch
#         this:
#           -- https://www.youtube.com/watch?v=k2P9yWSMaXE
#      in slowed-down time and really pay attention to the intersections.
#      The below implementation of Fortune's Algorithm is not particularly quick
#      due to the nature of the way its solved here, but it does allow for
#      easy visualization of the generation of the diagram
#      (and a little extra work will show the parabolas/sweepline moving too).
#   2) Also, thsi implementation has some errors in that some edges fail to be
#      created properly (i.e a corner is miised so there is a line where one 
#      shouldnt be) due to the nature of this computation. Also, some edges of
#      bordering seeds may not be EXACTLY lined up (but they're close). A "fix"
#      for this is slowing down the increments (sweepline_step). This does "
#      create a large efficiency problem and anything below .1 or so can be
#      way too slow to be practical if enough seeds are put in
#      (ex: 30 seeds, .1 step --> "
#   2) THIS IS IMPORTANT! The number of seeds used and the seed padding matters.
#      If the number of seeds is too large, the computation of the diagram
#      will take a very long time (somewhere around 70 takes a couple minutes)
#      depending on your machine. The seed padding will keep seeds from
#      generating closely, but too large a padding will also keep the seeds
#      from generating at all.
#   3) There is a small WIP piece that would improve efficiency, but it has not
#      been implemented at this time. It is the "complete" seed. Completed seeds
#      will be ignored when testing the seeds for intersections (see test_seeds)
#      and will save recourses. Again, this is WIP and is not yet implemented.

class Voronoi(object):
    def __init__(self, width, height, number_of_seeds, seed_padding):
        self.width = width
        self.height = height
        self.number_of_seeds = number_of_seeds
        self.seed_padding = seed_padding

        self.sweepline_height = 0
        self.sweepline_step = .1
        self.sweepline = shapes.Line((0, self.sweepline_height), 0)

        try:
            self.generate_seed_points()
            self.generate_seeds()
        except:
            raise Exception("Too many seeds and/or too much padding")
        self.generate_borderlines()

    #The following is the random seed generation. It will attempt to place
    #all of the seeds, if it can't it will recurse to try again until it
    #either succeeds or overflows. The last method is to generate the borders
    #of the diagram.
    ############################################################################
    def generate_seed_points(self):
        points = list()

        #So it doesn't get stuck in an infinite loop.
        max_iterations = 5000
        iterations = 0

        #Below is the attempt to make all the desired points.
        #----------------------------------------------------------------------#
        #Tries to place seeds within the border of the diagram (adding padding)
        #and padding distance awa from each other.
        while (len(points) < self.number_of_seeds and
               iterations < max_iterations):
            iterations += 1

            #Piacks random (x, y) point in the plane.
            x = random.randrange(self.seed_padding,
                                 (self.width - self.seed_padding))
            y = random.randrange(self.seed_padding,
                                 (self.height - self.seed_padding))
            point = (x, y)


            point_invalid = False
            for other_point in points:
                if isnear(point, other_point, self.seed_padding):
                    point_invalid = True

            if not point_invalid:
                points.append(point)
        #----------------------------------------------------------------------#

        if iterations >= max_iterations:
            self.generate_seed_points() #didn't work, try again

        self.points = points

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
    ############################################################################

    #The following set of methods is used in solving the diagram. It uses
    #Fortune's Algorithm (see above) to move a sweepline and generate parabolas
    #for each seed. It then updates (or adjusts --> see seed.adjust) each seed
    #to find legal intersections (see valid_intersection for more on legality)
    ############################################################################
    def solve(self):
        #Arbitrary height chosen as a stopping point
        #(most or maybe all diagrams will be solved by that point).
        while self.sweepline_height < self.height * 1.75:
            self.move_sweepline(self.sweepline_step)

    def solve_visually(self):
        #Unlike solve, solve_visually only goes through a single iteration
        #of the sweepline step. This is useful for polling the diagram
        #for its current state when drawing.
        if self.sweepline_height > self.height * 1.75:
            return None

        else:
            self.move_sweepline(self.sweepline_step)

            seed_points = list()
            for seed in self.seeds:
                if seed.active: #see test_seeds for definition of "active"
                    points = seed.poll_flattened_points()
                    seed_points.extend(points)

            return seed_points

    def move_sweepline(self, dy):
        self.sweepline_height += dy
        self.sweepline.y = self.sweepline_height
        self.test_seeds()

    def test_seeds(self):
        #This runs through each seed and checks for active-ness. An active seed
        #is a seed that is below the sweepline. If a seed is active, it will
        #be "adjusted" (see seed.adjust) to check for legal intersections
        #(see valid_intersection for definition of legality). 
        for seed in self.seeds:
            if not seed.active and self.sweepline > seed.pos:
                seed.activate(self.sweepline_height, self.borderlines)

            if not seed.complete and seed.active:
                seed.adjust(self.sweepline_height, self.seeds, self.borderlines)

    def valid_intersection(self, intersection):
        #A valid intersection is one that is 
        return (self.intersection_in_bounds(intersection) and
                self.intersection_is_edge(intersection))

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

    def activate(self, sweepline_height, borderlines):
        self.active = True
        self.parabola = shapes.Parabola(sweepline_height, self.pos)
        for border in borderlines:
            line = borderlines[border]
            self.intersections[line] = [None, None]

    def adjust(self, sweepline_height, other_seeds, borderlines):
        self.parabola.directrix = sweepline_height
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
