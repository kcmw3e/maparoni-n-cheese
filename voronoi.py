import shapes
import component
import pyglet
import random

class Voronoi(object):
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
                seed = Voronoi_seed(point, color)
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
        self.vectors = list()
        for seed in self.seeds:
            for other_seed in self.seeds:
                if seed != other_seed:
                    if seed.intersects(other_seed):
                        seed.intersecting_seeds.add(other_seed)
                    intersections = seed.intersections(other_seed)
                    seed.intersections_with_other_seeds = intersections
                    seed.deal_with_other_seeded_intersections()
                    for i in range(len(intersections)):
                        j = i - 1
                        intersection = intersections[i]
                        previous_intersection = intersections[j]
                        (x1, y1) = intersection
                        (x2, y2) = previous_intersection
                        self.lines.extend([x1, y1, x2, y2])
                    for v in seed.vectors:
                        (x1, y1) = v.beginning_point
                        (x2, y2) = v.endpoint
                        self.lines.extend([x1, y1, x2, y2])
        self.lines = pyglet.graphics.vertex_list(len(self.lines)//2, ("v2f", self.lines), ("c3B", [0,0,0]*(len(self.lines)//2)))

    def draw(self):
        self.batch.draw()
        self.lines.draw(pyglet.gl.GL_LINES)

class Voronoi_seed(object):
    def __init__(self, pos, color):
        self.pos = pos
        self.color = tuple(color)
        self.radius = 25
        self.make_shape()
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B", self.color * (len(self.shape.triangular_points) // 2))
        self.intersecting_seeds = set()
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

    def deal_with_other_seeded_intersections(self):
        self.perimeter_vectors = list()
        self.vectors = list()
        for i in range(len(self.intersections_with_other_seeds)):
            j = i - 1
            (x1, y1) = self.intersections_with_other_seeds[i]
            (x2, y2) = self.intersections_with_other_seeds[j]
            dx = x2 - x1
            dy = y2 - y1
            vector = shapes.Vector((x1, y1), (dx, dy))
            self.perimeter_vectors.append(vector)
        (x1, y1) = self.pos
        for vector in self.perimeter_vectors:
            for (x2, y2) in (vector.beginning_point, vector.endpoint):
                dx = x2 - x1
                dy = y2 - y1
                new_vector = shapes.Vector((x1, y1), (dx, dy))
                for v in self.perimeter_vectors:
                    if new_vector != v and new_vector.intersects(v):
                        (x2, y2) = new_vector.intersection(v)
                        dx = x2 - x1
                        dy = y2 - y1
                        if dx == 0 and dy == 0:
                            continue
                        new_vector = shapes.Vector((x1, y1), (dx, dy))
                self.vectors.append(new_vector)

def is_near(p1, p2, nearness = 50):
    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1 - x2) < nearness and abs(y1 - y2) < nearness