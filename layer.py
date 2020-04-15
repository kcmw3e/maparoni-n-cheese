import pyglet
import shapes

class Layer(object):
    def __init__(self, width, height, region_width = 300, region_height = 300):
        self.width = width
        self.height = height
        self.region_width = region_width
        self.region_height = region_height
        self.generate_regions()

    def generate_regions(self):
        regions_rows = self.height // self.region_height
        regions_cols = self.width // self.region_width
        if self.height % self.region_height != 0:
            regions_rows += 1
        if self.width % self.region_width != 0:
            regions_cols += 1
        self.regions = [["" for _ in range(regions_cols)] for _ in range(regions_rows)]
        for row in range(regions_rows):
            for col in range(regions_cols):
                x = col * self.region_width + self.region_width / 2
                y = row * self.region_height + self.region_height / 2
                pos = (x, y)
                self.regions[row][col] = Region(pos, self.region_width, self.region_height)

    def get_region_at_pos(self, pos):
        (x, y) = pos
        regions_row = y // self.region_height
        regions_col = x // self.region_width
        return self.regions[regions_row][regions_col]

    def add(self, map_object):
        for row in self.regions:
            for region in row:
                if region.object_in_region(map_object):
                    region.add(map_object)

    def add_if_not_intersecting(self, map_object):
        for row in self.regions:
            for region in row:
                if region.object_in_region(map_object):
                    if region.objects_in_region_intersect(map_object):
                        return False
        self.add(map_object)
        return True

    def draw(self):
        for row in self.regions:
            for region in row:
                region.draw()

    def update(self, width, height):
        old_regions = self.regions
        self.height = height
        self.width = width
        self.generate_regions()

        for row in range(len(old_regions)):
            for col in range(len(old_regions[row])):
                self.regions[row][col] = old_regions[row][col]

class Region(object):
    def __init__(self, pos, width, height):
        self.batch = pyglet.graphics.Batch()
        self.pos = pos
        self.width = width
        self.height = height
        self.objects = set()
        self.shape = shapes.Rect(self.pos, self.width, self.height)
        self.vertex_list = pyglet.graphics.vertex_list(4, ("v2f", self.shape.flattened_points), ("c3B", [100, 100, 100] * 4))

    def __repr__(self):
        return f"Region ({self.width, self.height}) at {self.pos}"

    def add(self, map_object):
        self.objects.add(map_object)

        for co in map_object.components:
            self.batch.add(co.number_of_points, pyglet.gl.GL_TRIANGLES, None, co.vertices, co.vertices_colors)
 
    def object_in_region(self, map_object):
        for component in map_object.components:
            if component.intersects(self):
                return True
        return False

    def draw(self):
        self.vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
        self.batch.draw()

    def objects_in_region_intersect(self, map_object):
        for obj in self.objects:
            if obj.intersects(map_object):
                return True
        return False
