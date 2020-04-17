import pyglet
import shapes

class GUI(object):
    def __init__(self, pos, width, height, background_color, button_functions, button_parameters, button_labels, button_colors):
        self.pos = pos
        self.width = width
        self.height = height
        self.background_color = background_color
        self.batch = pyglet.graphics.Batch()
        self.generate_background()

        self.hovered = False

        self.button_functions = button_functions
        self.button_parameters = button_parameters
        self.button_labels = button_labels
        self.button_height = 20
        self.button_width = 70
        self.button_padding = 20
        self.button_colors = button_colors
        self.button_border_color = [0, 0, 0]
        self.button_hover_color = [100, 0, 80]

        self.generate_buttons()

    def generate_background(self):
        self.background_shape = shapes.Rect(self.pos, self.width, self.height)
        self.background_vertices = ("v2f", self.background_shape.triangular_points)
        self.background_vertices_colors = (f"c{len(self.background_color)}B", self.background_color * (len(self.background_shape.triangular_points) // 2))
        self.background = self.batch.add(len(self.background_shape.triangular_points) // 2, pyglet.gl.GL_TRIANGLES, None, self.background_vertices, self.background_vertices_colors)

    def generate_buttons(self):
        self.buttons = list()
        for i in range(len(self.button_functions)):
            function = self.button_functions[i]
            parameters = self.button_parameters[i]
            label = self.button_labels[i]
            color = self.button_colors[i]
            x = i * (self.button_width + self.button_padding) + self.button_width / 2 + self.button_padding
            y = self.pos[1]
            pos = (x, y)
            b = Button(function, parameters, pos, label, self.button_width, self.button_height, color, self.button_border_color, self.button_hover_color)
            self.buttons.append(b)
            b.vertex_list = self.batch.add(len(b.shape.triangular_points) // 2, pyglet.gl.GL_TRIANGLES, None, b.vertices, b.vertices_colors)
            b.border_vertex_list = self.batch.add(len(b.shape.lines_points) // 2, pyglet.gl.GL_LINES, None, b.border_vertices, b.border_vertices_colors)
            b.label = pyglet.text.Label(b.label_name,
                          font_name='Times New Roman',
                          font_size=10,
                          x=b.pos[0], y=b.pos[1],
                          anchor_x='center', anchor_y='center', batch = self.batch, color = [0,0,0,255])

    def has_cursor(self, cursor_pos):
        return self.background_shape.contains_point(cursor_pos)

    def cursor_hovered(self, cursor_pos, clicked = False):
        for button in self.buttons:
            if button.shape.contains_point(cursor_pos):
                button.hovered()
                if clicked:
                    button()
            else:
                button.unhovered()

    def show_help_menu(self, show):
        pass

    def draw(self):
        self.batch.draw()

class Button(object):
    def __init__(self, function, parameters, pos, label_name, width, height, color, border_color, hover_color):
        self.function = function
        self.parameters = parameters
        self.label_name = label_name
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.border_color = border_color
        self.hover_color = hover_color
        self.shape = shapes.Rect(self.pos, self.width, self.height)
        self.vertices = ("v2f", self.shape.triangular_points)
        self.vertices_colors = (f"c{len(self.color)}B", self.color * (len(self.shape.triangular_points) // 2))
        self.border_vertices = ("v2f", self.shape.lines_points)
        self.border_vertices_colors = (f"c{len(self.border_color)}B", self.border_color * (len(self.shape.lines_points) // 2))

    def __call__(self):
        self.function(*self.parameters)

    def hovered(self):
        self.vertex_list.colors = self.hover_color * (len(self.shape.triangular_points) // 2)

    def unhovered(self):
        self.vertex_list.colors = self.color * (len(self.shape.triangular_points) // 2)
