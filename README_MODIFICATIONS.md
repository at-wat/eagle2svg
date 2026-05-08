# eagle2svg Modifications

This is a modified version of [eagle2svg](https://github.com/at-wat/eagle2svg) v0.1.5 with added support for rendering buses in Eagle schematic files.

## Changes Made

### 1. Implemented Bus Class (`eagle2svg/eagle_element.py`)

**Original code (line 1195-1197):**
```python
class Bus(object):
    def __init__(self, data):
        pass
```

**Modified code:**
```python
class Bus(object):
    def __init__(self, data):
        self.name = data['@name']
        self.segments = []
        if 'segment' in data:
            for segment_data in eagle_types.array(data['segment']):
                self.segments.append(Segment(segment_data))

    def render(self,
               view_box=None):
        for segment in self.segments:
            segment.render(view_box=view_box,
                           net_name=self.name)
```

### 2. Fixed Plain Parsing and Rendering in Sheet (`eagle2svg/eagle_element.py`)

**Original code (line ~1253-1260):**
```python
class Sheet(object):
    def __init__(self, data):
        self.plains = []
        ...
        for plain_data in eagle_types.named_array(data['plain']):
            self.plains.append(Plain(plain_data))
```

**Modified code:**
```python
class Sheet(object):
    def __init__(self, data):
        self.plain = Plain(data['plain'])
        ...
```

**Modified Sheet.render() method:**
```python
self.plain.render(view_box=view_box,
                 replace=replace)
```

The original code incorrectly used `named_array()` on the plain section, which caused it to extract the first child element (e.g., a text element) instead of passing the entire plain container. This prevented text annotations and other plain drawing elements from being parsed and rendered. The fix aligns with how the Board class handles plain sections.

### 3. Added Bus Rendering to Sheet (`eagle2svg/eagle_element.py`)

**Modified Sheet.render() method (line ~1278-1279):**

Added bus rendering loop:
```python
for bus in self.busses:
    bus.render(view_box=view_box)
```

This ensures buses are rendered alongside nets in the schematic output.

### 4. Fixed Multi-line Text Positioning (`eagle2svg/eagle_element.py`)

**Original code (line ~172-177):**
```python
height = len(lines) * size
if anchor == 'start':
    transforms = transforms \
        + ' translate(%f 0)' % (len_max * size * 0.65)
elif anchor == 'end':
    transforms = transforms \
        + ' translate(%f 0)' % (-len_max * size * 0.65)
```

**Modified code:**
```python
height = len(lines) * size
# For multi-line text, no extra translation needed
# The tspans have their own text-anchor attribute set to 'align'
# which handles the positioning correctly at x="0"
```

The original code incorrectly added horizontal translations for multi-line text. For 'start' (left-aligned) text, it shifted text to the right, causing misalignment. Since each `<tspan>` element already has its own `text-anchor` attribute, no additional translation is needed - the SVG text-anchor mechanism handles alignment correctly.

### 5. Added 5% Whitespace Margin (`eagle2svg/eagle_parser.py`)

**Modified viewBox calculation in both Schematic.render() and Board.render():**

**Original code:**
```python
view_box.x1 = view_box.x1 - 1
view_box.y1 = view_box.y1 - 1
view_box.x2 = view_box.x2 + 1
view_box.y2 = view_box.y2 + 1
```

**Modified code:**
```python
# Add 5% margin around the schematic
width = view_box.x2 - view_box.x1
height = view_box.y2 - view_box.y1
margin_x = width * 0.05
margin_y = height * 0.05
view_box.x1 = view_box.x1 - margin_x
view_box.y1 = view_box.y1 - margin_y
view_box.x2 = view_box.x2 + margin_x
view_box.y2 = view_box.y2 + margin_y
```

This adds a 5% whitespace margin around all schematics and boards for better visual presentation.

## Impact

- **Before**:
  - Text annotations and other plain drawing elements were not rendered in SVG/PDF output
  - Buses (thick blue lines representing signal groups) were not rendered in SVG/PDF output
  - Multi-line text annotations were incorrectly positioned (shifted to the right for left-aligned text)
  - Schematics had minimal (1 unit) margins, appearing cramped
- **After**:
  - Text annotations, wires, circles, rectangles, and all other plain elements are now properly rendered
  - Buses are now properly rendered, showing all bus connections and labels
  - Multi-line text annotations are correctly positioned according to their alignment
  - Schematics have 5% whitespace margins for better visual presentation

## Upstream

These changes should ideally be contributed back to the upstream eagle2svg project. The implementation closely follows the existing Net class pattern, making it a natural fit for the codebase.

## Version

Based on: eagle2svg v0.1.5
Modified: October 2025
Repository: https://github.com/at-wat/eagle2svg
