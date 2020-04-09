################################################################################
#
#   app.py
#   Code by: Casey Walker
#
################################################################################

import pyglet

class App(pyglet.window.Window):
    def __init__(self, width = 640, height = 480):
        config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer = True) #gets rid of anti-aliasing
        super(App, self).__init__(config = config, resizable = True, width = width, height = height)
        self.cursor_pos = tuple()
        self.moved_pos = tuple()
        self.previous_pos = tuple()


    def on_enter(self):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.cursor_pos = (x, y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.cursor_pos = (x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor_pos = (x, y)
        self.moved_pos = (dx, dy)
        self.previous_pos = (self.cursor_pos[0] + dx, self.cursor_pos[1] - dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor_pos = (x, y)
        self.moved_pos = (dx, dy)
        self.previous_pos = (self.cursor_pos[0] + dx, self.cursor_pos[1] - dy)

    def on_draw(self):
        self.clear()