# eagle2svg
Eagle cad to SVG converter.

eagle2svg helps social coding based circuit development.
It is easy to upload and embed drawings to the pull-request comment
by using [gh-pr-comment](https://github.com/at-wat/gh-pr-comment).

## Install

```
$ pip install --user eagle2svg
```

## Usage

```
eagle2svg eagle-file [sheet# [layer# [layer# ...]]]
```

- sheet#: schematic sheet index (for board layout rendering, set 0)
  - default: `0`
- layer#: visible layer index
  - default: `1 16 17 18 19 20 21 22 25 26 29 30 91 92 93 94 95 96 97 104`
  - e.g. board top layers: `1 20 17 18 21 25 19`
  - e.g. board bottom layers: `16 20 17 18 22 26 19`

## License

This package is released under BSD license.
