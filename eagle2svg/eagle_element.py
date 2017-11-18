import math
import copy

import svg_common
import eagle_types

COLOR = {
        1: 'maroon',
        15: 'gray',
        16: 'navy',
        17: 'green',
        18: 'green',
        19: 'olive',
        20: 'gray',
        21: 'gray',
        22: 'gray',
        25: 'gray',
        26: 'gray',
        91: 'green',
        92: 'navy',
        93: 'maroon',
        94: 'maroon',
        95: 'gray',
        96: 'gray',
        97: 'gray',
        104: 'gray'
        }
COLOR_MIRROR = {
        1: 16,
        16: 1
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
        xy.mirror = not xy.mirror
        ang = -ang
    sin = math.sin(ang)
    cos = math.cos(ang)
    xy.x = orig.x * cos - orig.y * sin + trans.x
    xy.y = orig.x * sin + orig.y * cos + trans.y

def align_mirror(align):
    if align == 'start':
        return 'end'
    elif align == 'end':
        return 'start'
    return align

def curve_radius(xy1, xy2, curve):
    mid = Vec2r((xy1.x + xy2.x) * 0.5, (xy1.y + xy2.y) * 0.5)
    if curve < 0:
        curve = -180 - curve
    else:
        curve = 180 - curve
    tan = math.tan(math.radians(curve) * 0.5)
    offset = Vec2r((xy1.y - xy2.y) * 0.5 * tan, -(xy1.x - xy2.x) * 0.5 * tan)
    cx = mid.x + offset.x
    cy = mid.y + offset.y
    r = math.hypot(cx - xy1.x, cy - xy1.y)
    return r

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

def render_text(text, xy, size, color,
        mirror_text = False,
        align = 'start',
        valign = 0.0):

    rot = xy.rot
    if xy.rot >= 180:
        if not mirror_text:
            xy.mirror = not xy.mirror
        ang = math.radians(xy.rot)
        ang = ang + math.pi / 2
        sin = math.sin(ang)
        cos = math.cos(ang)
        xy.x = xy.x + cos * size
        xy.y = xy.y + sin * size
    if xy.rot >= 90 and 270 > xy.rot:
        xy.rot = xy.rot - 180

    transforms = ''
    transforms = transforms + ' translate(%f %f)' % (xy.x, -xy.y)
    transforms = transforms + ' rotate(%f 0 0)' % (xy.rot)
    anchor = align
    if mirror_text:
        if xy.mirror:
            transforms = transforms + ' scale(-1 1)'
        if rot >= 180:
            anchor = align_mirror(anchor)
    else:
        if xy.mirror:
            anchor = align_mirror(anchor)

    text_option = ''
    lines = text.split('\n')
    if len(lines) <= 1:
        text2 = text
        height = size
        text_option = ' text-anchor="%s"' % anchor
    else:
        text2 = ''
        y2 = 0.0

        for line in lines:
            text2 = text2 + '<tspan x="0" y="%f" height="%f" text-anchor="%s">' % (
                    y2, size, align) + line + '</tspan>'
            y2 = y2 + size
        height = y2
        text_option = ' height="0" width="0"'
    
    if valign != 0.0:
        transforms = transforms + ' translate(0 %f)' % (-height * valign)

    return '<text fill="%s" font-size="%f" transform="%s"%s>%s</text>' % (
            color, size,
            transforms,
            text_option,
            text2)

class Wire(object):
    def __init__(self, data):
        self.x1 = float(data['@x1'])
        self.y1 = float(data['@y1'])
        self.x2 = float(data['@x2'])
        self.y2 = float(data['@y2'])
        self.width = float(data['@width'])
        if self.width < 0.05:
            self.width = 0.05
        if '@curve' in data:
            self.curve = float(data['@curve'])
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
                if hasattr(self, 'curve'):
                    r = curve_radius(xy1, xy2, self.curve)
                    if self.curve < 0:
                        side = 1
                    else:
                        side = 0
                    yield '<path d="M %f %f A %f %f 0 0 %d %f %f" fill="none" stroke="%s" stroke-width="%f" stroke-linecap="round"/>' % (
                            xy1.x, -xy1.y, r, r, side, xy2.x, -xy2.y, COLOR[self.layer], self.width)
                else:
                    yield '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-width="%f" stroke-dasharray="%s" stroke-linecap="round"/>' % (
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
                fill = 'none'
                if self.width == 0.0:
                    fill = COLOR[self.layer]
                yield '<circle cx="%f" cy="%f" r="%f" fill="%s" stroke="%s" stroke-width="%f"/>' % (
                        xy.x, -xy.y,
                        self.radius, fill, COLOR[self.layer], self.width)

class Pad(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.drill = float(data['@drill'])
        if '@diameter' in data:
            self.diameter = float(data['@diameter'])
        else:
            self.diameter = self.drill + 0.3
        self.shape = 'round'
        if '@shape' in data:
            self.shape = data['@shape']
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
            view_box = svg_common.ViewBox()):
        xy = Vec2r(self.x, self.y)
        rotate(xy, Vec2r(x, y), rot, mirror)
        view_box.expand(xy.x - self.diameter, -xy.y - self.diameter)
        view_box.expand(xy.x + self.diameter, -xy.y + self.diameter)
        yield '<circle cx="%f" cy="%f" r="%f" fill="green" stroke="none"/>' % (
                xy.x, -xy.y,
                self.diameter / 2.0)
        yield '<circle cx="%f" cy="%f" r="%f" fill="black" stroke="none"/>' % (
                xy.x, -xy.y,
                self.drill / 2.0)

class Hole(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.drill = float(data['@drill'])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        xy = Vec2r(self.x, self.y)
        rotate(xy, Vec2r(x, y), rot, mirror)
        view_box.expand(xy.x - self.drill, -xy.y - self.drill)
        view_box.expand(xy.x + self.drill, -xy.y + self.drill)
        yield '<circle cx="%f" cy="%f" r="%f" fill="none" stroke="gray" stroke-width="0.05"/>' % (
                xy.x, -xy.y,
                self.drill / 2.0)

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

class Smd(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.dx = float(data['@dx'])
        self.dy = float(data['@dy'])
        self.layer = int(data['@layer'])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            view_box = svg_common.ViewBox()):
        layer = self.layer
        if mirror:
            layer = COLOR_MIRROR[layer]
        if layer in layers:
            if layer in COLOR:
                xy1 = Vec2r(self.x - self.dx / 2, self.y - self.dy / 2)
                xy2 = Vec2r(self.x - self.dx / 2, self.y + self.dy / 2)
                xy3 = Vec2r(self.x + self.dx / 2, self.y + self.dy / 2)
                xy4 = Vec2r(self.x + self.dx / 2, self.y - self.dy / 2)
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
                        COLOR[layer])

class Polygon(object):
    def __init__(self, data):
        self.width = float(data['@width'])
        self.layer = int(data['@layer'])
        self.vertex = []
        for v in data['vertex']:
            if '@curve' in v:
                self.vertex.append([Vec2r(float(v['@x']), float(v['@y'])), float(v['@curve'])])
            else:
                self.vertex.append([Vec2r(float(v['@x']), float(v['@y']))])
        self.vertex.append(self.vertex[0])

    def render(self,
            layers = {},
            x = 0.0,
            y = 0.0,
            rot = 0,
            mirror = False,
            signal_fill = False,
            view_box = svg_common.ViewBox()):
        if self.layer in layers:
            if self.layer in COLOR:
                option = ''
                if signal_fill:
                    option = ' fill-opacity="0.25" stroke-opacity="0.5"'

                xyr = copy.deepcopy(self.vertex[0][0])
                rotate(xyr, Vec2r(x, y), rot, mirror)
                view_box.expand(xyr.x, -xyr.y)
                yield '<path d="M%f %f ' % (xyr.x, -xyr.y)
                xy_prev = copy.deepcopy(xyr)
                curve = 0.0
                next_curve = False
                for v in self.vertex:
                    xyr = copy.deepcopy(v[0])
                    rotate(xyr, Vec2r(x, y), rot, mirror)
                    view_box.expand(xyr.x, -xyr.y)
                    if next_curve:
                        next_curve = False
                        r = curve_radius(xy_prev, xyr, curve)
                        if curve < 0:
                            side = 1
                        else:
                            side = 0
                        yield 'A%f %f 0 0 %d %f %f ' % (r, r, side, xyr.x, -xyr.y)
                    else:
                        yield 'L%f %f ' % (xyr.x, -xyr.y)
                    xy_prev = copy.deepcopy(xyr)
                    if len(v) > 1:
                        next_curve = True
                        curve = v[1]
                yield 'Z" stroke="%s" fill="%s" stroke-width="%f"%s/>' % (
                        COLOR[self.layer], COLOR[self.layer], self.width, option)

class Text(object):
    def __init__(self, data):
        self.x = float(data['@x'])
        self.y = float(data['@y'])
        self.size = float(data['@size'])
        self.font = ''
        if '@font' in data:
            self.font = data['@font']
        self.align = 'start'
        self.valign = 0.0
        if '@align' in data:
            align = data['@align'].split('-')
            if align[0] == 'top':
                self.valign = 1.0
            elif align[0] == 'top':
                self.valign = 0.0
            else:
                self.valign = 0.5

            if align[1] == 'left':
                self.align = 'start'
            elif align[1] == 'right':
                self.align = 'end'
            else:
                self.align = 'middle'
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
            mirror_text = False,
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
                yield render_text(text,
                        xy,
                        self.size,
                        COLOR[self.layer],
                        mirror_text = mirror_text,
                        align = self.align,
                        valign = self.valign)

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
            yield render_text(self.name, xy, 2.0, 'gray', valign = 0.5)

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


class VisualElementBase(object):
    def __init__(self, data):
        self.wires = []
        self.circles = []
        self.holes = []
        self.pads = []
        self.vias = []
        self.rectangles = []
        self.polygons = []
        self.texts = []
        self.frames = []
        self.pins = []
        self.smds = []
        self.signal_fill = False
        if 'wire' in data:
            for wire_data in eagle_types.array(data['wire']):
                self.wires.append(Wire(wire_data))
        if 'circle' in data:
            for circle_data in eagle_types.array(data['circle']):
                self.circles.append(Circle(circle_data))
        if 'hole' in data:
            for hole_data in eagle_types.array(data['hole']):
                self.holes.append(Hole(hole_data))
        if 'pad' in data:
            for pad_data in eagle_types.array(data['pad']):
                self.pads.append(Pad(pad_data))
        if 'via' in data:
            for via_data in eagle_types.array(data['via']):
                self.vias.append(Pad(via_data))
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
        if 'smd' in data:
            for smd_data in eagle_types.array(data['smd']):
                self.smds.append(Smd(smd_data))

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
            mirror_text = False,
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
        for hole in self.holes:
            for output in hole.render(layers = layers,
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
                    signal_fill = self.signal_fill,
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
        for smd in self.smds:
            for output in smd.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for pad in self.pads:
            for output in pad.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for via in self.vias:
            for output in via.render(layers = layers,
                    x = x,
                    y = y,
                    rot = rot,
                    mirror = mirror,
                    view_box = view_box):
                yield output
        for text in self.texts:
            if not smashed or text.text[0] != '>':
                for output in text.render(layers = layers,
                        x = x,
                        y = y,
                        rot = rot,
                        mirror = mirror,
                        mirror_text = mirror_text,
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
                        mirror_text = mirror_text,
                        replace = replace,
                        view_box = view_box):
                    yield output

class Package(VisualElementBase):
    def __init__(self, data):
        super(Package, self).__init__(data)
        self.name = data['@name']

class Symbol(VisualElementBase):
    def __init__(self, data):
        super(Symbol, self).__init__(data)
        self.name = data['@name']

class Signal(VisualElementBase):
    def __init__(self, data):
        super(Signal, self).__init__(data)
        self.name = data['@name']
        self.signal_fill = True

class Plain(VisualElementBase):
    def __init__(self, data):
        super(Plain, self).__init__(data)

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
        self.packages = {}
        if 'symbols' in data:
            for symbol_data in eagle_types.named_array(data['symbols']):
                symbol = Symbol(symbol_data)
                self.symbols[symbol.name] = symbol
        if 'devicesets' in data:
            for deviceset_data in eagle_types.named_array(data['devicesets']):
                deviceset = Deviceset(deviceset_data)
                self.devicesets[deviceset.name] = deviceset
        if 'packages' in data:
            for package_data in eagle_types.named_array(data['packages']):
                package = Package(package_data)
                self.packages[package.name] = package

class Part(object):
    def __init__(self, data):
        self.name = data['@name']
        self.library = data['@library']
        self.deviceset = data['@deviceset']
        self.device = data['@device']
        if '@value' in data:
            self.value = data['@value']


class Element(object):
    def __init__(self, data):
        self.name = data['@name']
        self.value = data['@value']
        self.library = data['@library']
        self.package = data['@package']
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
            replace = {},
            mirror_text = False,
            view_box = svg_common.ViewBox()):
        replace2 = copy.deepcopy(replace)
        library = libraries[self.library]
        replace2['>NAME'] = self.name
        replace2['>VALUE'] = self.value

        for output in library.packages[self.package].render(
                layers = layers,
                x = self.x, y = self.y,
                rot = self.rot,
                mirror = self.mirror,
                replace = replace2,
                mirror_text = mirror_text,
                view_box = view_box,
                smashed = self.smashed,
                attributes = self.attributes):
            yield output

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
