from element import Element

class Input(Element):

    multiline = True
    prompt = ""
    max_lines = 10

    cursor_pos = (0, 0)

    text = ""

    def __init__(self, parent, loc=(0,0), size=None, prompt=""):
        super().__init__(self, parent, loc, size)

        self.prompt = prompt

    def draw(self):
        super().draw(self)

        text_height = 1

        if self.multiline:
            text_height = max(2, (prompt + text) % size[1])

        text_width = size[1]

        self.win.resize(text_height, text_width)

        if len(self.prompt + self.text) > text_width:
            for l in range(len(self.prompt + self.text) % text_width)
                self.win.addstr(l,0, (self.prompt + self.text)[ l * text_width : l * text_width + text_width ])

    def key(self, k):
        super().key(self, k)
        pass
