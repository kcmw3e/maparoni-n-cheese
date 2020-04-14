################################################################################
#
#   app.py
#   Code by: Casey Walker
#
################################################################################

import pyglet

class App(pyglet.window.Window):
    def __init__(self, width = 640, height = 480):
        config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer = True) #for anti-aliasing
        super(App, self).__init__(config = config, resizable = True,
                                  width = width, height = height)
        self.cursor_pos = tuple()
        self.moved_pos = tuple()
        self.previous_pos = tuple()

    def on_key_press(self, symbol, modifiers):
        pass

    def on_resize(self, width, height):
        #from: https://pyglet.readthedocs.io/en/latest/programming_guide/gl.html
        #this is what the default on_resize does when on_resize isn't defined
        ########################################################################
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        ########################################################################

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