import pyglet
from pyglet.gl import GL_TRIANGLES
import shapes
import map_obj

class Layer(object):
    def __init__(self, width, height, color, region_width = 300, region_height = 300):
        self.width = width
        self.height = height
        self.color = color
        self.region_width = region_width
        self.region_height = region_height
        self.batch = pyglet.graphics.Batch()
        self.generate_background()
        self.generate_regions()

    def generate_background(self):
        self.shape = shapes.Rect((self.width / 2, self.height / 2), self.width, self.height)
        self.num_points = len(self.shape.triangular_points) // 2
        self.background_vertices = ("v2f", self.shape.triangular_points)
        self.background_vertices_colors = (f"c4B", self.color * self.num_points)
        self.background = self.batch.add(self.num_points, GL_TRIANGLES, None, 
                                         self.background_vertices, 
                                         self.background_vertices_colors)

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
                region = Region(pos, width, height, self)
                self.regions.append(region)
                total_height += height
                y += height
            total_width += width
            x += width
            total_height = 0
            y = 0

    def get_region_at_pos(self, pos):
        for region in self.regions:
            if region.shape.contains_point(pos):
                return region

    def get_obj_at_pos(self, pos):
        region = self.get_region_at_pos(pos)
        return region.get_obj_at_pos(pos)

    def add(self, map_obj):
        for region in self.regions:
            if region.object_in_region(map_obj):
                region.add(map_obj)

    def add_if_not_intersecting(self, map_obj):
        for region in self.regions:
            if region.object_in_region(map_obj):
                if region.objects_in_region_intersect(map_obj):
                    return False
        self.add(map_obj)
        return True

    def remove_obj(self, map_obj):
        for region in self.regions:
            if map_obj in region.objects:
                region.objects.remove(map_obj)

    def draw(self):
        self.batch.draw()
    
    def toggle_grid(self, show):
        if show:
            visibility = 255
        else:
            visibility = 0
        for region in self.regions:
            region.change_visibility(visibility)

class Region(object):
    def __init__(self, pos, width, height, parent):
        self.pos = pos
        self.width = width
        self.height = height
        self.objects = set()
        self.border_color = [100, 100, 100, 0]
        self.shape = shapes.Rect(self.pos, self.width, self.height)
        self.num_points = len(self.shape.lines_points) // 2
        self.vertex_list = parent.batch.add(self.num_points, pyglet.gl.GL_LINES,
                             None, ("v2f", self.shape.lines_points), 
                             ("c4B", self.border_color * self.num_points))

    def __repr__(self):
        return f"Region ({self.width, self.height}) at {self.pos}"

    def add(self, map_obj):
        self.objects.add(map_obj)
 
    def object_in_region(self, map_obj):
        for component in map_obj.components:
            if component.for_collision and component.intersects(self):
                return True
        return False

    def objects_in_region_intersect(self, map_obj):
        for obj in self.objects:
            if obj.intersects(map_obj):
                return True
        return False

    def get_obj_at_pos(self, pos):
        for obj in self.objects:
            for component in obj.components:
                if component.shape.contains_point(pos):
                    return obj
        return None

    def change_visibility(self, visibility):
        for i in range(3, len(self.vertex_list.colors), 4):
            self.vertex_list.colors[i] = visibility