import math
import copy

import svg_common
import eagle_types

COLOR = {
        1: 'maroon',
        16: 'navy',
        17: 'green',
        18: 'green',
        19: 'olive',
        20: 'gray',
        21: 'gray',
        22: 'gray',
        25: 'gray',
        26: 'gray',
        29: 'gray',
        30: 'gray',
        91: 'green',
        92: 'navy',
        93: 'maroon',
        94: 'maroon',
        95: 'gray',
        96: 'gray',
        97: 'gray',
        104: 'gray'
        }

PIN_LENGTH = {
	'long':   7.62,
	'middle': 5.08,
	'short':  2.54,
	'point':  0.0
        }

class Vec2r(object):
    def __init__(self, x, y, rot = 0, mirror = False):
        self.x = copy.deepcopy(x)
        self.y = copy.deepcopy(y)
        self.rot = copy.deepcopy(rot)
        self.mirror = copy.deepcopy(mirror)

def rotate(xy, trans, rot, mirror = False):
    orig = copy.deepcopy(xy)
    ang = math.radians(rot)
    if mirror:
        orig.x = -orig.x
    sin = math.sin(ang)
    cos = math.cos(ang)
    xy.x = orig.x * cos - orig.y * sin + trans.x
    xy.y = orig.x * sin + orig.y * cos + trans.y

def rotate_text(xy, trans, rot, mirror = False):
    orig = copy.deepcopy(xy)
    ang = math.radians(rot)
    if mirror:
        orig.x = -orig.x
        xy.mirror = not xy.mirror
        xy.rot = -xy.rot
        if xy.rot < 0:
            xy.rot += 360
        ang = -ang
    sin = math.sin(ang)
    cos = math.cos(ang)
    xy.x = orig.x * cos - orig.y * sin + trans.x
    xy.y = orig.x * sin + orig.y * cos + trans.y
    if mirror:
        xy.rot = xy.rot - rot
    else:
        xy.rot = xy.rot + rot
    if xy.rot >= 360:
        xy.rot -= 360
    if xy.rot < 0:
        xy.rot += 360

def render_text(text, xy, size, color):
    MIRROR_TEXT_ANCHOR = {
            False: "start",
            True: "end"
            }

    if xy.rot >= 180:
        xy.mirror = not xy.mirror
        ang = math.radians(xy.rot)
        if xy.mirror:
            ang = ang + math.pi / 2
        else:
            ang = ang + math.pi / 2
        sin = math.sin(ang)
        cos = math.cos(ang)
        xy.x = xy.x + cos * size
        xy.y = xy.y + sin * size
    if xy.rot >= 90 and 270 > xy.rot:
        xy.rot = xy.rot - 180
    return '<text fill="%s" font-size="%f" x="%f" y="%f" transform="rotate(%f %f %f)" text-anchor="%s">%s</text>' % (
            color, size, xy.x, -xy.y,
            xy.rot, xy.x, -xy.y,
            MIRROR_TEXT_ANCHOR[xy.mirror],
            text)

class Wire(object):
    def __init__(self, data):
        self.x1 = float(data['@x1'])
        self.y1 = float(data['@y1'])
        self.x2 = float(data['@x2'])
        self.y2 = float(data['@y2'])
        self.width = float(data['@width'])
        self.layer = int(data['@layer'])
        self.style = ''
        self.stroke_dasharray = ''
        if '@style' in data:
            self.style = data['@style']
            if self.style == 'shortdash':
                self.stroke_dasharray = '1,1'
            elif self.style == 'longdash':
                self.stroke_dasharray = '2,2'
            elif self.style == 'dashdot':
                self.stroke_dasharray = '0.5,0.5'

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                xy1 = Vec2r(self.x1, self.y1)
                xy2 = Vec2r(self.x2, self.y2)
                rotate(xy1, Vec2r(x, y), rot, mirror)
                rotate(xy2, Vec2r(x, y), rot, mirror)
                view_box.expand(xy1.x, -xy1.y)
                view_box.expand(xy2.x, -xy2.y)
                yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="%f" stroke-dasharray="%s"/>' % (
                        xy1.x, -xy1.y, xy2.x, -xy2.y,
                        COLOR[self.layer], self.width, self.stroke_dasharray)

class Junction(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])

    def render(self,
            layers = {},
            view_box = svg_common.ViewBox()):
        view_box.expand(self.x, -self.y)
        yield '<circle cx="%f" cy="%f" r="0.5" fill="green"/>' % (self.x, -self.y)

class Label(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.size = float(data['@size'])
        self.layer = int(data['@layer'])
        self.rot = 0
        self.mirror = False
        if '@rot' in data:
            if data['@rot'][0] == 'M':
                self.mirror = True
                if data['@rot'][1] == 'R':
                    self.rot = int(data['@rot'][2:])
            elif data['@rot'][0] == 'R':
                self.rot = int(data['@rot'][1:])

    def render(self,
            layers = {},
            view_box = svg_common.ViewBox(),
            net_name = ''):
        if self.layer in layers:
            if self.layer in COLOR:
                xy = Vec2r(0.0, 0.0)
                rotate_text(xy, Vec2r(self.x, self.y), self.rot, self.mirror)
                view_box.expand(xy.x, -xy.y)
                yield render_text(net_name, xy, self.size, COLOR[self.layer])


class Circle(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.radius = float(data['@radius'])
        self.width = float(data['@width'])
        self.layer = int(data['@layer'])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                xy = Vec2r(self.x, self.y)
                rotate(xy, Vec2r(x, y), rot, mirror)
                view_box.expand(xy.x - self.radius, -xy.y - self.radius)
                view_box.expand(xy.x + self.radius, -xy.y + self.radius)
                yield '<circle cx="%f" cy="%f" r="%f" fill="%s" stroke="%s" stroke-width="%f"/>' % (
                        xy.x, -xy.y,
                        self.radius, COLOR[self.layer], COLOR[self.layer], self.width)

class Pad(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.drill = float(data['@drill'])

class Rectangle(object):
    def __init__(self, data):
        self.x1 = float(data['@x1'])
        self.y1 = float(data['@y1'])
        self.x2 = float(data['@x2'])
        self.y2 = float(data['@y2'])
        self.layer = int(data['@layer'])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                xy1 = Vec2r(self.x1, self.y1)
                xy2 = Vec2r(self.x2, self.y1)
                xy3 = Vec2r(self.x2, self.y2)
                xy4 = Vec2r(self.x1, self.y2)
                rotate(xy1, Vec2r(x, y), rot, mirror)
                rotate(xy2, Vec2r(x, y), rot, mirror)
                rotate(xy3, Vec2r(x, y), rot, mirror)
                rotate(xy4, Vec2r(x, y), rot, mirror)
                view_box.expand(xy1.x, -xy1.y)
                view_box.expand(xy2.x, -xy2.y)
                view_box.expand(xy3.x, -xy3.y)
                view_box.expand(xy4.x, -xy4.y)
                yield '<polygon points="%f,%f %f,%f %f,%f %f,%f" fill="%s"/>' % (
                        xy1.x, -xy1.y, xy2.x, -xy2.y, xy3.x, -xy3.y, xy4.x, -xy4.y,
                        COLOR[self.layer])

class Polygon(object):
    def __init__(self, data):
        self.width = float(data['@width'])
        self.layer = int(data['@layer'])
        self.vertex = []
        for v in data['vertex']:
            self.vertex.append(Vec2r(float(v['@x']), float(v['@y'])))

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                yield '<polygon stroke="%s" fill="%s" stroke-width="%f" points="' % (
                        COLOR[self.layer], COLOR[self.layer], self.width)
                for xy in self.vertex:
                    xyr = copy.deepcopy(xy)
                    rotate(xyr, Vec2r(x, y), rot, mirror)
                    view_box.expand(xyr.x, -xyr.y)
                    yield '%f,%f ' % (xyr.x, -xyr.y)
                yield '"/>'

class Text(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.size = float(data['@size'])
        if '@font' in data:
            self.font = data['@font']
        self.text = ''
        if '#text' in data:
            self.text = data['#text']
        self.layer = int(data['@layer'])
        self.rot = 0
        self.mirror = False
        if '@rot' in data:
            if data['@rot'][0] == 'M':
                self.mirror = True
                if data['@rot'][1] == 'R':
                    self.rot = int(data['@rot'][2:])
            elif data['@rot'][0] == 'R':
                self.rot = int(data['@rot'][1:])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            replace = {},
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                xy = Vec2r(self.x, self.y, self.rot, self.mirror)
                rotate_text(xy, Vec2r(x, y), rot, mirror)
                view_box.expand(xy.x, -xy.y)
                text = self.text
                if self.text.upper() in replace:
                    text = replace[self.text]
                yield render_text(text, xy, self.size, COLOR[self.layer])

class Pin(object):
    def __init__(self, data):
        self.name = data['@name']
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.visible = 'both'
        if '@visible' in data:
            self.visible = data['@visible']
        self.length = data['@length']
        self.rot = 0
        self.mirror = False
        if '@rot' in data:
            if data['@rot'][0] == 'M':
                self.mirror = True
                if data['@rot'][1] == 'R':
                    self.rot = int(data['@rot'][2:])
            elif data['@rot'][0] == 'R':
                self.rot = int(data['@rot'][1:])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            replace = {},
            connects = {},
            view_box = svg_common.ViewBox()):
        xy1 = Vec2r(0.0, 0.0)
        xy2 = Vec2r(PIN_LENGTH[self.length], 0.0)
        rotate(xy1, Vec2r(self.x, self.y), self.rot, self.mirror)
        rotate(xy2, Vec2r(self.x, self.y), self.rot, self.mirror)
        rotate(xy1, Vec2r(x, y), rot, mirror)
        rotate(xy2, Vec2r(x, y), rot, mirror)
        view_box.expand(xy1.x, -xy1.y)
        view_box.expand(xy2.x, -xy2.y)
        yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="maroon" stroke-width="0.15"/>' % (
                xy1.x, -xy1.y, xy2.x, -xy2.y)

        if self.visible == 'pin' or self.visible == 'both':
            xy = Vec2r(PIN_LENGTH[self.length] + 1.5, -0.5)
            rotate_text(xy, Vec2r(self.x, self.y), self.rot, self.mirror)
            rotate_text(xy, Vec2r(x, y), rot, mirror)
            yield render_text(self.name, xy, 2.0, 'gray')

        if self.visible == 'pad' or self.visible == 'both':
            xy = Vec2r(1.0, 0.0)
            rotate_text(xy, Vec2r(self.x, self.y), self.rot, self.mirror)
            rotate_text(xy, Vec2r(x, y), rot, mirror)
            yield render_text(connects[self.name].pad, xy, 1.5, 'gray')


class Frame(object):
    def __init__(self, data):
        self.x1 = float(data['@x1'])
        self.y1 = float(data['@y1'])
        self.x2 = float(data['@x2'])
        self.y2 = float(data['@y2'])
        self.columns = int(data['@columns'])
        self.rows = int(data['@rows'])
        self.layer = int(data['@layer'])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                xy1 = Vec2r(self.x1, self.y1)
                xy2 = Vec2r(self.x2, self.y1)
                xy3 = Vec2r(self.x2, self.y2)
                xy4 = Vec2r(self.x1, self.y2)
                rotate(xy1, Vec2r(x, y), rot, mirror)
                rotate(xy2, Vec2r(x, y), rot, mirror)
                rotate(xy3, Vec2r(x, y), rot, mirror)
                rotate(xy4, Vec2r(x, y), rot, mirror)
                view_box.expand(xy1.x, -xy1.y)
                view_box.expand(xy2.x, -xy2.y)
                view_box.expand(xy3.x, -xy3.y)
                view_box.expand(xy4.x, -xy4.y)
                yield '<polygon points="%f,%f %f,%f %f,%f %f,%f" stroke="%s" stroke-width="0.2" fill="none"/>' % (
                        xy1.x, -xy1.y, xy2.x, -xy2.y, xy3.x, -xy3.y, xy4.x, -xy4.y,
                        COLOR[self.layer])
                xy1 = Vec2r(self.x1 + 4, self.y1 + 4)
                xy2 = Vec2r(self.x2 - 4, self.y1 + 4)
                xy3 = Vec2r(self.x2 - 4, self.y2 - 4)
                xy4 = Vec2r(self.x1 + 4, self.y2 - 4)
                rotate(xy1, Vec2r(x, y), rot, mirror)
                rotate(xy2, Vec2r(x, y), rot, mirror)
                rotate(xy3, Vec2r(x, y), rot, mirror)
                rotate(xy4, Vec2r(x, y), rot, mirror)
                yield '<polygon points="%f,%f %f,%f %f,%f %f,%f" stroke="%s" stroke-width="0.1" fill="none"/>' % (
                        xy1.x, -xy1.y, xy2.x, -xy2.y, xy3.x, -xy3.y, xy4.x, -xy4.y,
                        COLOR[self.layer])
                col_span = ((self.x2 - 4) - (self.x1 + 4)) / self.columns
                for ix in range(1, self.columns):
                    xy1 = Vec2r(self.x1 + ix * col_span + 4, self.y1)
                    xy2 = Vec2r(self.x1 + ix * col_span + 4, self.y1 + 4)
                    rotate(xy1, Vec2r(x, y), rot, mirror)
                    rotate(xy2, Vec2r(x, y), rot, mirror)
                    yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="0.1"/>' % (
                            xy1.x, -xy1.y, xy2.x, -xy2.y, COLOR[self.layer])
                    xy1 = Vec2r(self.x1 + ix * col_span + 4, self.y2)
                    xy2 = Vec2r(self.x1 + ix * col_span + 4, self.y2 - 4)
                    rotate(xy1, Vec2r(x, y), rot, mirror)
                    rotate(xy2, Vec2r(x, y), rot, mirror)
                    yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="0.1"/>' % (
                            xy1.x, -xy1.y, xy2.x, -xy2.y, COLOR[self.layer])
                for ix in range(1, self.columns + 1):
                    xy = Vec2r(self.x1 + (ix - 0.5) * col_span + 4 - 1.5, self.y1 + 1)
                    rotate(xy, Vec2r(x, y), rot, mirror)
                    yield render_text(str(ix), xy, 3.0, COLOR[self.layer])
                    xy = Vec2r(self.x1 + (ix - 0.5) * col_span + 4 - 1.5, self.y2 -3)
                    rotate(xy, Vec2r(x, y), rot, mirror)
                    yield render_text(str(ix), xy, 3.0, COLOR[self.layer])
                row_span = ((self.y2 - 4) - (self.y1 + 4)) / self.rows
                for iy in range(1, self.rows):
                    xy1 = Vec2r(self.x1, self.y1 + iy * row_span + 4)
                    xy2 = Vec2r(self.x1 + 4, self.y1 + iy * row_span + 4)
                    rotate(xy1, Vec2r(x, y), rot, mirror)
                    rotate(xy2, Vec2r(x, y), rot, mirror)
                    yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="0.1"/>' % (
                            xy1.x, -xy1.y, xy2.x, -xy2.y, COLOR[self.layer])
                    xy1 = Vec2r(self.x2, self.y1 + iy * row_span + 4)
                    xy2 = Vec2r(self.x2 - 4, self.y1 + iy * row_span + 4)
                    rotate(xy1, Vec2r(x, y), rot, mirror)
                    rotate(xy2, Vec2r(x, y), rot, mirror)
                    yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="0.1"/>' % (
                            xy1.x, -xy1.y, xy2.x, -xy2.y, COLOR[self.layer])
                for iy in range(1, self.rows + 1):
                    xy = Vec2r(self.x1 + 0.5, self.y1 + (iy - 0.5) * row_span + 4 - 1)
                    rotate(xy, Vec2r(x, y), rot, mirror)
                    yield render_text(chr(ord('A') + self.rows - iy), xy, 3.0, COLOR[self.layer])
                    xy = Vec2r(self.x2 - 3.5, self.y1 + (iy - 0.5) * row_span + 4 - 1)
                    rotate(xy, Vec2r(x, y), rot, mirror)
                    yield render_text(chr(ord('A') + self.rows - iy), xy, 3.0, COLOR[self.layer])


class Symbol(object):
    def __init__(self, data):
        self.name = data['@name']
        self.wires = []
        self.circles = []
        self.pads = []
        self.rectangles = []
        self.polygons = []
        self.texts = []
        self.frames = []
        self.pins = []
        if 'wire' in data:
            for wire_data in eagle_types.array(data['wire']):
                self.wires.append(Wire(wire_data))
        if 'circle' in data:
            for circle_data in eagle_types.array(data['circle']):
                self.circles.append(Circle(circle_data))
        if 'pad' in data:
            for pad_data in eagle_types.array(data['pad']):
                self.pads.append(Pad(pad_data))
        if 'rectangle' in data:
            for rectangle_data in eagle_types.array(data['rectangle']):
                self.rectangles.append(Rectangle(rectangle_data))
        if 'polygon' in data:
            for polygon_data in eagle_types.array(data['polygon']):
                self.polygons.append(Polygon(polygon_data))
        if 'text' in data:
            for text_data in eagle_types.array(data['text']):
                self.texts.append(Text(text_data))
        if 'frame' in data:
            for frame_data in eagle_types.array(data['frame']):
                self.frames.append(Frame(frame_data))
        if 'pin' in data:
            for pin_data in eagle_types.array(data['pin']):
                self.pins.append(Pin(pin_data))

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            replace = {},
            connects = {},
            view_box = svg_common.ViewBox(),
            smashed = False,
            attributes = {}):
        for wire in self.wires:
            for output in wire.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for circle in self.circles:
            for output in circle.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for rectangle in self.rectangles:
            for output in rectangle.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for polygon in self.polygons:
            for output in polygon.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for frame in self.frames:
            for output in frame.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for pin in self.pins:
            for output in pin.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    connects = connects,
                    view_box = view_box):
                yield output
        for text in self.texts:
            if not smashed or text.text[0] != '>':
                for output in text.render(layers = layers,
                        x = x,
                        y = y,
                        rot = rot,
                        mirror = mirror,
                        replace = replace,
                        view_box = view_box):
                    yield output
        if smashed:
            for name, attribute in attributes.items():
                text = copy.deepcopy(attribute)
                text.text = '>' + name;
                text.x = 0
                text.y = 0
                text.rot = 0
                text.mirror = False
                for output in text.render(layers = layers,
                        x = attribute.x,
                        y = attribute.y,
                        rot = attribute.rot,
                        mirror = attribute.mirror,
                        replace = replace,
                        view_box = view_box):
                    yield output

class Gate(object):
    def __init__(self, data):
        self.name = data['@name']
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.symbol = data['@symbol']

class Connect(object):
    def __init__(self, data):
        self.gate = data['@gate']
        self.pin = data['@pin']
        self.pad = data['@pad']

class Device(object):
    def __init__(self, data):
        self.name = data['@name']
        self.connects = {}
        if 'connects' in data:
            for connect_data in eagle_types.named_array(data['connects']):
                connect = Connect(connect_data)
                self.connects[connect.pin] = connect

class Deviceset(object):
    def __init__(self, data):
        self.name = data['@name']
        self.uservalue = False
        if '@uservalue' in data:
            if data['@uservalue'] == 'yes':
                self.uservalue = True
        self.gates = {}
        self.devices = {}
        for gate_data in eagle_types.named_array(data['gates']):
            gate = Gate(gate_data)
            self.gates[gate.name] = gate
        for device_data in eagle_types.named_array(data['devices']):
            device = Device(device_data)
            self.devices[device.name] = device


class Library(object):
    def __init__(self, data):
        self.name = data['@name']
        self.symbols = {}
        self.devicesets = {}
        for symbol_data in eagle_types.named_array(data['symbols']):
            symbol = Symbol(symbol_data)
            self.symbols[symbol.name] = symbol
        for deviceset_data in eagle_types.named_array(data['devicesets']):
            deviceset = Deviceset(deviceset_data)
            self.devicesets[deviceset.name] = deviceset

class Part(object):
    def __init__(self, data):
        self.name = data['@name']
        self.library = data['@library']
        self.deviceset = data['@deviceset']
        self.device = data['@device']
        if '@value' in data:
            self.value = data['@value']


class Plain(object):
    def __init__(self, data):
        self.name = ''

class Instance(object):
    def __init__(self, data):
        self.part = data['@part']
        self.gate = data['@gate']
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.mirror = False
        self.smashed = False
        self.rot = 0
        self.attributes = {}
        if '@rot' in data:
            if data['@rot'][0] == 'M':
                self.mirror = True
                if data['@rot'][1] == 'R':
                    self.rot = int(data['@rot'][2:])
            elif data['@rot'][0] == 'R':
                self.rot = int(data['@rot'][1:])
        if '@smashed' in data:
            if data['@smashed'] == 'yes':
                self.smashed = True
        if 'attribute' in data:
            for attribute_data in eagle_types.array(data['attribute']):
                self.attributes[attribute_data['@name']] = Text(attribute_data)

    def render(self,
            layers = {},
            libraries = {},
            parts = {},
            replace = {},
            view_box = svg_common.ViewBox()):
        replace2 = copy.deepcopy(replace)
        part = parts[self.part]
        library = libraries[part.library]
        deviceset = library.devicesets[part.deviceset]
        gate = deviceset.gates[self.gate]
        if len(deviceset.gates) > 1:
            replace2['>NAME'] = part.name + gate.name
        else:
            replace2['>NAME'] = part.name
        replace2['>VALUE'] = ''
        if hasattr(part, 'value'):
            replace2['>VALUE'] = part.value
        else:
            replace2['>VALUE'] = deviceset.name

        for output in library.symbols[gate.symbol].render(
                layers = layers,
                x = self.x, y = self.y,
                rot = self.rot,
                mirror = self.mirror,
                replace = replace2,
                connects = deviceset.devices[part.device].connects,
                view_box = view_box,
                smashed = self.smashed,
                attributes = self.attributes):
            yield output

class Busses(object):
    def __init__(self, data):
        pass

class Segment(object):
    def __init__(self, data):
        self.pinrefs = []
        self.wires = []
        self.junctions = []
        self.labels = []
        if 'wire' in data:
            for wire_data in eagle_types.array(data['wire']):
                self.wires.append(Wire(wire_data))
        if 'junction' in data:
            for junction_data in eagle_types.array(data['junction']):
                self.junctions.append(Junction(junction_data))
        if 'label' in data:
            for label_data in eagle_types.array(data['label']):
                self.labels.append(Label(label_data))

    def render(self,
            layers = {},
            view_box = svg_common.ViewBox(),
            net_name = ''):
        for wire in self.wires:
            for output in wire.render(layers = layers,
                    view_box = view_box):
                yield output
        for junction in self.junctions:
            for output in junction.render(layers = layers,
                    view_box = view_box):
                yield output
        for label in self.labels:
            for output in label.render(layers = layers,
                    view_box = view_box,
                    net_name = net_name):
                yield output

class Net(object):
    def __init__(self, data):
        self.name = data['@name']
        self.signal_class = int(data['@class'])
        self.segments = []
        for segment_data in eagle_types.array(data['segment']):
            self.segments.append(Segment(segment_data))

    def render(self,
            layers = {},
            view_box = svg_common.ViewBox()):
        for segment in self.segments:
            for output in segment.render(layers = layers,
                    view_box = view_box,
                    net_name = self.name):
                yield output


class Sheet(object):
    def __init__(self, data):
        self.plains = []
        self.instances = []
        self.busses = []
        self.nets = []
        for plain_data in eagle_types.named_array(data['plain']):
            self.plains.append(Plain(plain_data))
        for instance_data in eagle_types.named_array(data['instances']):
            self.instances.append(Instance(instance_data))
        for bus_data in eagle_types.named_array(data['busses']):
            self.busses.append(Bus(bus_data))
        for net_data in eagle_types.named_array(data['nets']):
            self.nets.append(Net(net_data))

    def render(self,
            layers = {},
            libraries = {},
            parts = {},
            replace = {},
            view_box = svg_common.ViewBox()):
        for net in self.nets:
            for output in net.render(layers = layers):
                yield output
        for instance in self.instances:
            for output in instance.render(layers = layers,
                    libraries = libraries,
                    parts = parts,
                    replace = replace,
                    view_box = view_box):
                yield output
