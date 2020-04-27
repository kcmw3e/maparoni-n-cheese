import pyglet

class Cursor(object):
    empty_fn = lambda: None
    def __init__(self, parent):
        self.parent = parent
        self.pos = (0, 0)
        self.function = Cursor.empty_fn
        self.args = [ ]
        self.visibility = True
        self.img = None
        self.type = None
        self.selected = None
        self.call_default = True
        self.dragged = False
        self.batch = pyglet.graphics.Batch()

    def __call__(self):
        if self.call_default:
            self.default_function(*self.default_args)
        elif self.function != Cursor.empty_fn:
            self.function(*self.args)

    def toggle_call_default(self, set_to = None):
        if set_to != None:
            self.call_default = set_to
        else:
            self.call_default = not self.call_default

    def toggle_visibility(self, set_to = None):
        if set_to != None:
            self.visibility = set_to
        else:
            self.visibility = not self.visibility
        self.parent.set_mouse_visible(self.visibility)

    def get_pos(self):
        return self.pos

    def draw(self):
        self.batch.draw()

    def delete_selected(self):
        self.selected.delete()
        self.selected = None

    def move(self, dx, dy):
        (x, y) = self.pos
        self.pos = (x + dx, y + dy)
        if self.selected != None:
            self.selected.move(dx, dy)

    def set_default(self, function, args):
        self.default_function = function
        self.default_args = args