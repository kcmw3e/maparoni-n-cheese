import pyglet
import shapes
import component

class Layer(object):
    def __init__(self, width, height, color, region_width = 300, region_height = 300):
        self.width = width
        self.height = height
        self.color = color
        self.region_width = region_width
        self.region_height = region_height
        self.generate_background()
        self.generate_regions()

    def generate_background(self):
        self.shape = shapes.Rect((self.width / 2, self.height / 2), self.width, self.height)
        self.background = component.Component(self.shape, self.color, pyglet.gl.GL_POLYGON)

    def generate_regions(self):
        self.regions = list()
        total_width = total_height = 0
        x = y = 0
        while total_width < self.width:
            if x + self.region_width <= self.width:
                width = self.region_width
            else:
                width = self.width - total_width
            while total_height < self.height:
                if y + self.region_height <= self.height:
                    height = self.region_height
                else:
                    height = self.height - total_height
                pos = (x + width / 2, y + height / 2)
                region = Region(pos, width, height)
                self.regions.append(region)
                total_height += height
                y += height
            total_width += width
            x += width
            total_height = 0
            y = 0

    def get_region_at_pos(self, pos):
        (x, y) = pos
        regions_row = y // self.region_height
        regions_col = x // self.region_width
        return self.regions[regions_row][regions_col]

    def add(self, map_object):
        for region in self.regions:
            if region.object_in_region(map_object):
                region.add(map_object)

    def add_if_not_intersecting(self, map_object):
        for region in self.regions:
            if region.object_in_region(map_object):
                if region.objects_in_region_intersect(map_object):
                    return False
        self.add(map_object)
        return True

    def draw(self):
        self.background.vertex_list.draw(self.background.draw_type)
        for region in self.regions:
            region.draw()

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
        for component in map_object.components:
            self.batch.add(component.number_of_points, pyglet.gl.GL_TRIANGLES, None, component.vertices, component.vertices_colors)
 
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
