import xmltodict
import copy
import os
from datetime import datetime

import svg_common
import eagle_element
import eagle_types

class EagleFileBase(object):
    def __init__(self, data):
        self.parts = {}
        self.libraries = {}
        for part_data in eagle_types.named_array(data['parts']):
            part = eagle_element.Part(part_data)
            self.parts[part.name] = part
        for library_data in eagle_types.named_array(data['libraries']):
            library = eagle_element.Library(library_data)
            self.libraries[library.name] = library

class Board(EagleFileBase):
    def __init__(self, data):
        super(Schematic, self).__init__(data)

class Schematic(EagleFileBase):
    def __init__(self, data):
        super(Schematic, self).__init__(data)

        self.sheets = []

        for sheet_data in eagle_types.named_array(data['sheets']):
            self.sheets.append(eagle_element.Sheet(sheet_data))

    def render(self,
            sheet = 0,
            layers = {},
            replace = {}):
        replace2 = copy.deepcopy(replace)
        replace2['>SHEET'] = str(sheet + 1) + '/' + str(len(self.sheets))
        view_box = svg_common.ViewBox()
        svg_contents = ''
        for output in self.sheets[sheet].render(layers = layers,
                libraries = self.libraries,
                parts = self.parts,
                replace = replace2,
                view_box = view_box):
            svg_contents = svg_contents + output

        print('<?xml version="1.0"?>')
        print('<svg version="1.2" xmlns="http://www.w3.org/2000/svg" viewBox="%f %f %f %f">' % (
            view_box.x1, view_box.y1, view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))
        print('<style type="text/css">:root{background-color: white;} *{font-family:Arial,Helvetica;}</style>')
        print('%s' % svg_contents)
        print('</svg>')


class Eagle(object):
    def __init__(self, filename):
        f = open(filename)
        data = xmltodict.parse(f.read())

        self.layers = data['eagle']['drawing']['layers']
        if 'schematic' in data['eagle']['drawing']:
            self.data = Schematic(data['eagle']['drawing']['schematic'])
        if 'board' in data['eagle']['drawing']:
            self.data = Board(data['eagle']['drawing']['board'])
        
        self.replace = {}
        self.replace['>DRAWING_NAME'], ext = os.path.splitext(os.path.basename(filename))
        self.replace['>LAST_DATE_TIME'] = datetime.fromtimestamp(os.path.getmtime(filename))

    def render(self, sheet = 0, layers = {}):
        return self.data.render(sheet = sheet,
                layers = layers,
                replace = self.replace)
