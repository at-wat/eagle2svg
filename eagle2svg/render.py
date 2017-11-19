from __future__ import print_function
import sys

import eagle2svg
from eagle2svg import eagle_parser


def render_main():
    argv = sys.argv
    if len(argv) < 2:
        print('eagle2svg %s' % eagle2svg.__version__)
        print('usage: eagle2svg eagle-file [sheet# [layer# [layer# ...]]]')
        print('- board top layers   : 1 20 17 18 21 25 19')
        print('- board bottom layers: 16 20 17 18 22 26 19')
        sys.exit()

    data = eagle_parser.Eagle(argv[1])
    if len(argv) > 2:
        sheet = int(argv[2])
    else:
        sheet = 0
    if len(argv) > 3:
        layers = {}
        for i in range(3, len(argv) - 1):
            layers[int(argv[i])] = True
    else:
        layers = {
            91: True, 92: True, 93: True, 94: True,
            95: True, 96: True, 97: True, 104: True,
            1: True, 16: True, 17: True, 18: True,
            19: True, 20: True, 21: True, 22: True,
            25: True, 26: True, 29: True, 30: True
        }

    data.render(sheet, layers)
