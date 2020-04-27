import pyglet
from pyglet.gl import GL_LINES, GL_TRIANGLES
import shapes

class GUI(object):
    def __init__(self, pos, width, height, background_color,
                 button_width, button_height, button_padding,
                 button_colors, button_hover_colors,
                 button_label_colors, button_labels, font_size, font,
                 button_functions, button_args):

        self.pos = pos
        self.width = width
        self.height = height
        self.background_color = background_color
        self.batch = pyglet.graphics.Batch()
        self.generate_background()
        self.hovered = False

        self.font = font
        self.font_size = font_size
        self.button_functions = button_functions
        self.button_args = button_args
        self.button_labels = button_labels
        self.button_label_colors = button_label_colors
        self.button_height = button_height
        self.button_width = button_width
        self.button_padding = button_padding
        self.button_colors = button_colors
        self.button_border_color = [0, 0, 0]
        self.button_hover_colors = button_hover_colors
        self.batch_labels = pyglet.graphics.Batch()
        self.generate_buttons()

    def generate_background(self):
        self.background_shape = shapes.Rect(self.pos, self.width, self.height)
        self.background_num_points = len(self.background_shape.triangular_points) // 2

        self.background_vertices = ("v2f", self.background_shape.triangular_points)
        self.background_vertices_colors = (f"c4B",
                                           self.background_color * self.background_num_points)

        self.background = self.batch.add(self.background_num_points, GL_TRIANGLES,
                                         None, self.background_vertices,
                                         self.background_vertices_colors)

    def generate_buttons(self):
        self.buttons = list()
        for i in range(len(self.button_functions)):
            function = self.button_functions[i]
            args = self.button_args[i]
            label = self.button_labels[i]
            color = self.button_colors[i]
            label_color = self.button_label_colors[i]
            hover_color = self.button_hover_colors[i]

            x = (i * (self.button_width     + self.button_padding) +
                      self.button_width / 2 + self.button_padding)
            y = self.pos[1]
            pos = (x, y)

            b = Button(function, args, pos, label,
                       self.button_width, self.button_height,
                       color, self.button_border_color, hover_color)

            self.buttons.append(b)

            b.vertex_list = self.batch.add(b.num_points, GL_TRIANGLES, None,
                                           b.vertices, b.vertices_colors)
            
            b.border_vertex_list = self.batch.add(b.num_border_points,
                                                  GL_LINES, None,
                                                  b.border_vertices, 
                                                  b.border_vertices_colors)

            b.label = pyglet.text.Label(b.label_name, font_name = self.font,
                                        font_size = self.font_size,
                                        x = b.pos[0], y = b.pos[1],
                                        anchor_x = 'center', anchor_y = 'center',
                                        batch = self.batch_labels, color = label_color)

    def check_hovered(self, cursor_pos):
        if self.background_shape.contains_point(cursor_pos):
            self.hovered = True
            self.cursor_hovered(cursor_pos)
        else:
            self.hovered = False

    def cursor_hovered(self, cursor_pos):
        for button in self.buttons:
            button.check_hovered(cursor_pos)

    def clicked(self):
        for button in self.buttons:
            if button.is_hovered:
                button()

    def show_help_menu(self, show):
        pass

    def draw(self):
        self.batch.draw()
        self.batch_labels.draw()

class Button(object):
    def __init__(self, function, args, pos, label_name, width, height,
                 color, border_color, hover_color):
        self.function = function
        self.args = args
        self.label_name = label_name
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.border_color = border_color
        self.hover_color = hover_color
        self.shape = shapes.Rect(self.pos, self.width, self.height)

        self.num_points = len(self.shape.triangular_points) // 2
        self.num_border_points = len(self.shape.lines_points) // 2
        self.vertices = ("v2f", self.shape.triangular_points)
        self.border_vertices = ("v2f", self.shape.lines_points)

        self.vertices_colors = (f"c{len(self.color)}B",
                                self.color * self.num_points)

        self.border_vertices_colors = (f"c{len(self.border_color)}B",
                                       self.border_color * self.num_border_points)

    def __call__(self):
        self.function(*self.args)

    def check_hovered(self, cursor_pos):
        if self.shape.contains_point(cursor_pos):
            self.is_hovered = True
            self.hovered()
        else:
            self.is_hovered = False
            self.unhovered()

    def hovered(self):
        self.vertex_list.colors = self.hover_color * self.num_points

    def unhovered(self):
        self.vertex_list.colors = self.color * self.num_points
