import shapes
import component
import pyglet
import random

class Voronoi(object):
    def __init__(self, width, height, number_of_seeds, seed_padding):
        self.width = width
        self.height = height
        self.number_of_seeds = number_of_seeds
        self.seed_padding = seed_padding
        self.sweepline_height = 0
        self.sweepline = shapes.Line((0, self.sweepline_height), 0)
        if self.generate_seed_points():
            self.generate_seeds()
        else:
            print("ERROR")
        self.generate_borderlines()

    def generate_seed_points(self, depth = 0):
        if depth > 500:
            return False
        points = list()
        max_iterations = 1000
        iterations = 0
        while len(points) < self.number_of_seeds and iterations < max_iterations:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            point = (x, y)
            if len(points) > 0:
                point_invalid = False
                for other_point in points:
                    """if (isnear(point, other_point, self.seed_padding) or
                        (self.seed_padding < x < self.width - self.seed_padding and
                        self.seed_padding < y < self.height - self.seed_padding)):"""
                    if isnear(point, other_point, self.seed_padding):
                            point_invalid = True
                if not point_invalid:
                    points.append(point)
            else:
                points.append(point)
            iterations += 1
        if iterations >= max_iterations:
            success = self.generate_seed_points(depth + 1)
            if not success:
                return False
        self.points = points
        return True

    def generate_seeds(self):
        self.seeds = list()
        for point in self.points:
            self.seeds.append(Voronoi_seed(point))

    def generate_borderlines(self):
        l_line = shapes.Line((0, 0), None)
        r_line = shapes.Line((self.width, 0), None)
        b_line = shapes.Line((0, 0), 0)
        t_line = shapes.Line((0, self.height), 0)
        self.borderlines = [l_line, r_line, b_line, t_line]

    def solve(self):
        while self.sweepline_height < self.height * 1.75:
            self.move_sweepline(.05)

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

class Voronoi_seed(object):
    def __init__(self, pos):
        self.pos = pos
        self.active = False
        self.complete = False
        self.parabola = None
        self.intersections = dict()
        self.border_intersections = dict()

    def __lt__(self, sweepline):
        return self.pos[1] < sweepline.point[1] #using the y-values

    def activate(self, sweepline, x_min, x_max, y_min, y_max, borderlines):
        self.active = True
        self.parabola = shapes.Parabola(sweepline, self.pos)
        self.parabola.open_domain(x_min, x_max)
        self.parabola.open_range(y_min, y_max)
        for line in borderlines:
            self.border_intersections[line] = [None, None]

    def adjust(self, sweepline, other_seeds, border_lines):
        self.parabola.directrix = sweepline
        for line in border_lines:
                intersections = self.parabola.intersections(line)
                for (i, intersection) in enumerate(intersections):
                    self.border_intersections[line][i] = intersection
        for seed in other_seeds:
            if seed.active and seed != self:
                intersections = self.parabola.intersections(seed.parabola)
                if seed not in self.intersections:
                    self.intersections[seed] = [None, None]
                for (i, intersection) in enumerate(intersections):
                    if (self.parabola.point_in_domain(intersection) and
                        self.parabola.point_in_range(intersection)):
                            invalid = False
                            for test_seed in other_seeds:
                                if (test_seed != self and test_seed != seed and 
                                    test_seed.active and 
                                    test_seed.parabola > intersection):
                                        invalid = True
                            if not invalid:
                                self.intersections[seed][i] = intersection

    def poll_points(self):
        points = list()
        for seed in self.intersections:
            for intersection in self.intersections[seed]:
                if intersection != None:
                    points.append(intersection)
        if len(points) == 0:
            return []
        points = ordered(self.pos, points)
        (x1, y1) = points[0]
        ordered_flattened_points = [x1, y1]
        for point in points[1:]:
            (x, y) = point
            ordered_flattened_points.extend([x, y] * 2)
        ordered_flattened_points.extend([x1, y1])
        return ordered_flattened_points

def isnear(point1, point2, nearness):
    (x1, y1) = point1
    (x2, y2) = point2
    return abs(x1 - x2) < nearness or abs(y1 - y2) < nearness

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

































class Circular_voronoi(object):
    def __init__(self, number_of_seeds, x_range, y_range, background_color):
        self.number_of_seeds = number_of_seeds
        self.x_range = x_range
        self.y_range = y_range
        self.background_color = background_color
        self.setup()

    def setup(self):
        self.batch = pyglet.graphics.Batch()
        self.make_background()
        self.seeds = list()
        self.make_seeds()
        self.lines = None

    def make_background(self):
        x = (self.x_range[1] + self.x_range[0]) / 2
        y = (self.y_range[1] + self.y_range[0]) / 2
        pos = (x, y)
        width = (self.x_range[1] - self.x_range[0])
        height = (self.y_range[1] - self.y_range[0])
        self.background_rect = shapes.Rect(pos, width, height)
        self.background_vertices = ("v2f", self.background_rect.flattened_points)
        self.background_vertices_colors = (f"c{len(self.background_color)}B", self.background_color * (len(self.background_rect.flattened_points) // 2))
        number_of_points = len(self.background_rect.flattened_points) // 2
        self.background_vertex_list = self.batch.add(number_of_points, pyglet.gl.GL_POLYGON, None, self.background_vertices, self.background_vertices_colors)

    def make_seeds(self):
        points = []
        loops = 0
        while len(points) <= self.number_of_seeds:
            loops += 1
            if loops > 100:
                self.setup()
                break
            x = random.randint(self.x_range[0], self.x_range[1])
            y = random.randint(self.y_range[0], self.y_range[1])
            point = (x, y)
            near = False
            for p in points:
                if is_near(point, p, 40):
                    near = True
            if near == True:
                continue
            else:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                a = 30
                color = [r, g, b, a]
                seed = Circular_voronoi_seed(point, color)
                seed.vertex_list = self.batch.add(len(seed.shape.triangular_points) // 2, pyglet.gl.GL_TRIANGLES, None, seed.vertices, seed.vertices_colors)
                seed.point = self.batch.add(1, pyglet.gl.GL_POINTS, None, ("v2f", [x,y]), ("c3b", [0, 0, 0]))
                self.seeds.append(seed)
                points.append(point)

    def increase_radii(self, dr):
        for seed in self.seeds:
            seed.increment_radius(dr)
        self.do_intersections()

    def do_intersections(self):
        self.lines = list()
        
        self.other_lines = list()

        self.vectors = list()
        for seed in self.seeds[:1]:
            seed_intersections = list()
            for other_seed in self.seeds:
                if seed != other_seed:
                    if seed.intersects(other_seed):
                        intersections = seed.intersections(other_seed)
                        seed_intersections.append(intersections)
                seed.deal_with_other_seeded_intersections(seed_intersections)
                self.lines.extend(seed.points)

                self.other_lines.extend(seed.other_points)
        self.other_lines = pyglet.graphics.vertex_list(len(self.other_lines)//2, ("v2f", self.other_lines), ("c3B", [100,100,100]*(len(self.other_lines)//2)))
        self.lines = pyglet.graphics.vertex_list(len(self.lines)//2, ("v2f", self.lines), ("c3B", [0,0,0]*(len(self.lines)//2)))

    def draw(self):
        self.batch.draw()
        self.lines.draw(pyglet.gl.GL_LINES)
        self.other_lines.draw(pyglet.gl.GL_LINES)

class Circular_voronoi_seed(object):
    def __init__(self, pos, color):
        self.pos = pos
        self.color = tuple(color)
        self.radius = 25
        self.make_shape()
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B", self.color * (len(self.shape.triangular_points) // 2))
        self.intersections_with_other_seeds = list()

    def __hash__(self):
        return hash((self.pos, self.color, "Voronoi_seed"))

    def increment_radius(self, dr):
        self.radius += dr
        self.make_shape()
        self.vertex_list.vertices = self.shape.triangular_points

    def make_shape(self):
        self.shape = shapes.Circle(self.pos, self.radius, 20)

    def intersects(self, other):
        if self.shape.intersects(other.shape):
            return True
        else:
            return False

    def intersections(self, other):
        return self.shape.intersections(other.shape)

    def deal_with_other_seeded_intersections(self, intersection_pairs):
        self.seed_intersection_vectors = list()
        for ((x1, y1), (x2, y2)) in intersection_pairs:
            dx = x2 - x1
            dy = y2 - y1
            vector = shapes.Vector((x1, y1), (dx, dy))
            self.seed_intersection_vectors.append(vector)

        radial_vectors = list()
        for vector in self.seed_intersection_vectors:
            for other_vector in self.seed_intersection_vectors:
                if vector.intersects(other_vector):
                    (x1, y1) = self.pos
                    (x2, y2) = vector.intersection(other_vector)
                    dx = x2 - x1
                    dy = y2 - y1
                    radial_vector = shapes.Vector((self.pos), ((dx, dy)))
                    radial_vector_crosses = 0
                    for v in self.seed_intersection_vectors:
                        if radial_vector.intersects(v) and not is_near(radial_vector.terminating_point, radial_vector.intersection(v), 1):
                            radial_vector_crosses += 1
                    if radial_vector_crosses < 1:
                        radial_vectors.append(radial_vector)

        for vector in self.seed_intersection_vectors:
            (x1, y1) = self.pos
            (x2, y2) = vector.beginning_point
            (x3, y3) = vector.terminating_point
            dx1 = x2 - x1
            dx2 = x3 - x1
            dy1 = y2 - y1
            dy2 = y3 - y1
            radial_vector1 = shapes.Vector((self.pos), (dx1, dy1))
            radial_vector2 = shapes.Vector((self.pos), (dx2, dy2))
            radial_vector1_crosses = 0
            radial_vector2_crosses = 0
            for vector in self.seed_intersection_vectors:
                if radial_vector1.intersects(vector) and not is_near(radial_vector1.terminating_point, radial_vector1.intersection(vector), 1):
                    radial_vector1_crosses += 1
                if radial_vector2.intersects(vector) and not is_near(radial_vector2.terminating_point, radial_vector2.intersection(vector), 1):
                    radial_vector2_crosses += 1
            if radial_vector1_crosses < 1:
                radial_vectors.append(radial_vector1)
            if radial_vector2_crosses < 1:
                radial_vectors.append(radial_vector2)

        new_vectors = list()
        for vector in radial_vectors:
            crosses = 0
            for other_vector in self.seed_intersection_vectors:
                if vector.intersects(other_vector) and not is_near(vector.terminating_point, vector.intersection(other_vector), .3):
                    crosses += 1
            if crosses < 1:
                new_vectors.append(vector)
        radial_vectors = new_vectors

        radial_vectors_by_angle = dict()
        radial_vectors_angles = list()
        for vector in radial_vectors:
            angle = vector.angle
            radial_vectors_by_angle[angle] = vector
            radial_vectors_angles.append(angle)

        points = list()
        new_radial_vectors = list()
        for angle in sorted(radial_vectors_angles):
            vector = radial_vectors_by_angle[angle]
            new_radial_vectors.append(vector)

        for i in range(len(new_radial_vectors)):
            j = i - 1
            vector1 = new_radial_vectors[i]
            vector2 = new_radial_vectors[j]
            (x1, y1) = vector1.terminating_point
            (x2, y2) = vector2.terminating_point          
            points.extend([x1, y1, x2, y2])

        other_points = list()
        for v in radial_vectors:
            (x1, y1) = v.beginning_point
            (x2, y2) = v.terminating_point
            other_points.extend([x1,y1,x2,y2])
        self.other_points = other_points

        self.points = points
        self.radial_vectors = new_radial_vectors

def is_near(p1, p2, nearness = 50):
    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1 - x2) < nearness and abs(y1 - y2) < nearness