class Element():

    # (y, x) -- (0,0) is top left corner
    location = (-1, -1)
    # (height, width)
    size = (-1, -1)
    layer = -1

    parent = None
    win = None

    def __init__(self, parent, loc=(0,0), size=None):
        self.location = loc
        if not size:
            self.size = parent.getmaxyx()
        else:
            self.size = size
        self.parent = parent
        self.der()

        self.win = self.parent.derwin(self.size[0], self.size[1], self.location[0], self.location[1])
        self.win.border(0)
        self.win.noutrefresh()

    def draw(self):
        pass

    def key(self, k):
        pass
