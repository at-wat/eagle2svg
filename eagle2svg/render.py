from __future__ import print_function
import sys

import __init__
import eagle_parser


def render_main(argv = []):
    if len(argv) < 2:
        print('eagle2svg %s' % __init__.__version__)
        print('usage: eagle2svg eagle-file')
        sys.exit()

    data = eagle_parser.Eagle(argv[1])
    data.render(0, {91: True, 92: True, 93: True, 94: True, 95: True, 96: True, 97: True, 104: True})
