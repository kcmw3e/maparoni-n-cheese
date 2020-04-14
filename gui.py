import pyglet
import shapes

class GUI(object):
    def __init__(self, pos, width, height, background_color):
        self.pos = pos
        self.width = width
        self.height = height
        self.background_color = background_color
        self.batch = pyglet.graphics.Batch()
        self.generate_background()

        self.generate_buttons()

    def generate_background(self):
        self.background_shape = shapes.Rect(self.pos, self.width, self.height)
        self.background_vertices = ("v2f", self.background_shape.triangular_points)
        self.background_vertices_colors = (f"c{len(self.background_color)}B", self.background_color * (len(self.background_shape.triangular_points) // 2))
        self.background = self.batch.add(len(self.background_shape.triangular_points) // 2, pyglet.gl.GL_TRIANGLES, None, self.background_vertices, self.background_vertices_colors)

    def generate_buttons(self):
        self.buttons = list()
        height = 20
        width = 40
        padding = 20
        for i in range(10):
            pos = (self.pos[0], self.pos[1]+height*i+padding*i)
            b = Button(pos, width, height, [235, 178, 103], "a")
            self.buttons.append(b)
            self.batch.add(len(b.shape.triangular_points)//2, pyglet.gl.GL_TRIANGLES, None, b.vertices, b.vertices_colors)
            self.batch.add(len(b.shape.points), pyglet.gl.GL_LINE_LOOP, None, ("v2f", b.shape.flattened_points), ("c3B",[0, 0,0]*len(b.shape.points)))

    def draw(self):
        self.batch.draw()

class Button(object):
    def __init__(self, pos, width, height, color, function):
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.function = function
        self.shape = shapes.Rect(self.pos, self.width, self.height)
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B", self.color * (len(self.shape.triangular_points) // 2))