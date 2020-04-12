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

    def add(self, thing):
        for row in self.regions:
            for region in row:
                if region.object_in_region(thing):
                    region.add(thing)

    def add_if_not_intersecting(self, thing):
        for row in self.regions:
            for region in row:
                if region.object_in_region(thing):
                    if region.objects_in_region_intersect(thing):
                        return False
        self.add(thing)
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
        for row in old_regions:
            for region in row:
                for obj in region.objects:
                    self.add_if_not_intersecting(obj)


class Region(object):
    def __init__(self, pos, width, height):
        self.batch = pyglet.graphics.Batch()#
        self.pos = pos
        self.width = width
        self.height = height
        self.objects = list()
        self.shape = shapes.Rect(self.pos, self.width, self.height)
        self.vertex_list = pyglet.graphics.vertex_list(4, ("v2f", self.shape.flattened_points), ("c3B", [100, 100, 100] * 4)) #*

    def __repr__(self):
        return f"Region ({self.width, self.height}) at {self.pos}"

    def add(self, thing):
        self.objects.append(thing)

        for co in thing.components:
            self.batch.add(co.number_of_points, pyglet.gl.GL_TRIANGLES, None, co.vertices, co.vertices_colors)
 
    def object_in_region(self, thing):
        for component in thing.components:
            if component.intersects(self):
                return True
        return False

    def draw(self):
        self.vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
        self.batch.draw()

    def objects_in_region_intersect(self, thing):
        for obj in self.objects:
            if obj.intersects(thing):
                return True
        return False
