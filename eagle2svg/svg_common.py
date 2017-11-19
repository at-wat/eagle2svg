class ViewBox(object):
    def __init__(self, x1=0.0, y1=0.0, x2=0.0, y2=0.0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.layers = {}

    def expand(self, x, y):
        if self.x1 > x:
            self.x1 = x
        if self.y1 > y:
            self.y1 = y
        if x > self.x2:
            self.x2 = x
        if y > self.y2:
            self.y2 = y

    def append(self, layer, svg):
        if layer not in self.layers:
            self.layers[layer] = []
        self.layers[layer].append(svg)
