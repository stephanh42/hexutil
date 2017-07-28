"""
Classes and functions to deal with hexagonal grids.

This module assumes that the hexagonal grid is aligned with the x-axis.
If you need it to be aligned with the y-axis instead, you will have to
swap x and y coordinates everywhere.
"""

from collections import namedtuple
import math

class Hex(namedtuple("Hex", "x y")):
    "A single hexagon in a hexagonal grid."""
    _neighbours = ((2, 0), (1, 1), (-1, 1), (-2, 0), (-1, -1), (1, -1))

    def is_valid(self):
        """Check if this hex is a valid hex."""
        x, y = self
        return (x + y) % 2 == 0

    def neighbours(self):
        """Return the 6 direct neighbours of this hex."""
        x, y = self
        return [Hex(x+dx, y+dy) for dx, dy in self._neighbours]

    def __add__(self, other):
        x1, y1 = self
        x2, y2 = other
        return Hex(x1+x2, y1+y2)

    def __sub__(self, other):
        x1, y1 = self
        x2, y2 = other
        return Hex(x1-x2, y1-y2)

    def __neg__(self):
        x, y = self
        return Hex(-x, -y)

    def distance(self, other):
        """Distance in number of hexagon steps.
        Direct neighbours of this hex have distance 1.
        """
        x1, y1 = self
        x2, y2 = other
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dy + max(0, (dx - dy)//2)

    def rotate_left(self):
        """Given a hex return the hex when rotated 60° counter-clock-wise around the origin.
        """
        x, y = self
        return Hex((x - 3 * y) >> 1, (x + y) >> 1)

    def rotate_right(self):
        """Given a hex return the hex when rotated 60° clock-wise around the origin.
        """
        x, y = self
        return Hex((x + 3 * y) >> 1, (y - x) >> 1)

origin = Hex(0, 0)

class HexGrid(namedtuple("HexGrid", "width height")):
    """Represents the dimensions of a hex grid as painted on the screen.
    The hex grid is assumed to be aligned horizontally, like so:
       / \ / \ / \ 
      |   |   |   |
       \ / \ / \ /
    The center of hex (0, 0) is assumed to be on pixel (0, 0).
    The hexgrid is determined by width and height, which are the screen coordinates
    of the upper-right corner of the central hex.

    To have equilateral hexes, width:height should be approximately √3 : 1.
    If you only pass in width to the constructor, the height is computed to be
    an integer as close as possible to width / √3 .
    """

    _hex_factor = math.sqrt(1.0/3.0)
    _corners = ((1, 1), (0, 2), (-1, 1), (-1, -1), (0, -2), (1, -1))

    def __new__(cls, width, height=None):
        if height is None:
            height = round(cls._hex_factor * width)
        return super().__new__(cls, width, height)

    def corners(self, hex):
        """Get the 6 corners (in pixel coordinates) of the hex."""
        width, height = self
        x0, y0 = hex
        y0 *= 3
        return [(width * (x + x0), height * (y + y0)) for x, y in self._corners]

    def center(self, hex):
        """Get the center (as (x, y) tuple) of a hexagon."""
        width, height = self
        x, y = hex
        return (x*width, 3*height*y)

    def hex_at_coordinate(self, x, y):
        """Given pixel coordinates x and y, get the hexagon under it."""
        width, height = self
        x0 = x // width
        δx = x % width
        y0 = y // (3 * height)
        δy = y % (3 * height)

        if (x0 + y0) % 2 == 0:
            if width * δy < height * (2 * width - δx):
                return Hex(x0, y0)
            else:
                return Hex(x0 + 1, y0 + 1)
        elif width * δy < height * (width + δx):
            return Hex(x0 + 1, y0)
        else:
            return Hex(x0, y0 + 1)
