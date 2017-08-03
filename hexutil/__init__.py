"""
Classes and functions to deal with hexagonal grids.

This module assumes that the hexagonal grid is aligned with the x-axis.
If you need it to be aligned with the y-axis instead, you will have to
swap x and y coordinates everywhere.
"""

from collections import namedtuple
from heapq import heappush, heappop
import operator
import math
import random

class InvalidHex(ValueError):
    pass

class Hex(namedtuple("Hex", "x y")):
    "A single hexagon in a hexagonal grid."""
    _neighbours = ((2, 0), (1, 1), (-1, 1), (-2, 0), (-1, -1), (1, -1))

    def __new__(cls, x, y):
        if (x + y) % 2 != 0:
            raise InvalidHex("x and y coordinate must sum to an even number")
        return super().__new__(cls, x, y)

    def neighbours(self):
        """Return the 6 direct neighbours of this hex."""
        x, y = self
        return [Hex(x+dx, y+dy) for dx, dy in self._neighbours]

    def random_neighbour(self, random=random):
        """Return a random neighbour of this hexagon."""
        x, y = self
        dx, dy = random.choice(self._neighbours)
        return Hex(x+dx, y+dy)

    def random_walk(self, N, random=random):
        """Yield random walk of length N.
        Returns a generator of length N+1 since it includes the start point.
        """
        position = self
        yield position
        for i in range(N):
            position = position.random_neighbour(random)
            yield position

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

    def field_of_view(self, transparent, max_distance, visible=None):
        """Calculate field-of-view.
        transparent  -- from a Hex to a boolean, indicating of the Hex is transparent
        max_distance -- maximum distance you can view
        visible      -- if provided, should be a dict which will be filled and returned

        Returns a dict which has as its keys the hexagons which are visible.
        The value is a bitmask which indicates which sides of the hexagon are visible.
        The bitmask is useful if you want to use this function also to compute light sources.

        view_set = player_pos.field_of_view(...)
        light_set = light_source.field_of_view(...)

        # Is pos visible?
        if view_set.get(pos, 0) & light_set.get(pos, 0):
            # yes it is
        """
        if visible is None:
            visible = {}
        visible[self] = all_directions
        for direction in range(6):
            _fovtree._field_of_view(self, direction, transparent, max_distance, visible)
        return visible

    def find_path(self, destination, passable, cost=lambda pos: 1):
        """Perform path-finding.
        self        -- Starting position for path finding.
        destination -- Destination position for path finding.
        passable    -- Function of one position, returning True if we can move through this hex.
        cost        -- cost function for moving through a hex. Should return a value ≥ 1. By default all costs are 1.
        """
        pathfinder = HexPathFinder(self, destination, passable, cost)
        pathfinder.run()
        return pathfinder.path


all_directions = (1 << 6) - 1
origin = Hex(0, 0)

Hex.rotations = (
        lambda x: x,
        operator.methodcaller("rotate_left"),
        lambda x: -x.rotate_right(),
        operator.neg,
        lambda x: -x.rotate_left(),
        operator.methodcaller("rotate_right")
        )

class _FovTree:
    _corners = ((0, -2), (1, -1), (1, 1), (0, 2))
    _neighbours = (Hex(1, -1), Hex(2, 0), Hex(1, 1))
    _cached_successors = None

    def __init__(self, hexagon, direction, angle1, angle2):
        self.hexagon = hexagon
        self.angle1 = angle1
        self.angle2 = angle2
        self.direction = direction
        self.hexagons = [rot(hexagon) for rot in Hex.rotations]
        self.distance = hexagon.distance(origin)

    def get_angle(self, corner):
        cx, cy = corner
        x, y = self.hexagon
        return (3*y + cy)/float(x + cx)

    def _field_of_view(self, offset, direction, transparent, max_distance, visible):
        if self.distance > max_distance:
            return
        hexagon = offset + self.hexagons[direction]
        if transparent(hexagon):
            visible[hexagon] = all_directions
            for succ in self.successors():
                succ._field_of_view(offset, direction, transparent, max_distance, visible)
        else:
            directions = 1 << ((self.direction + direction) % 6)
            visible[hexagon] = directions | visible.get(hexagon, 0)

    def successors(self):
        _cached_successors = self._cached_successors
        if _cached_successors is None:
            _cached_successors = []
            angles = [self.get_angle(c) for c in self._corners]
            hexagon = self.hexagon
            for i in range(3):
                c1 = max(self.angle1, angles[i])
                c2 = min(self.angle2, angles[i+1])
                if c1 < c2:
                    nb = self._neighbours[i]
                    _cached_successors.append(_FovTree(hexagon + nb, (i-1) % 6, c1, c2))
            self._cached_successors = _cached_successors

        return _cached_successors

_fovtree = _FovTree(Hex(2, 0), 0, -1.0, 1.0)

class Rectangle(namedtuple("Rectangle", "x y width height")):
    """Represents a rectangle.
    x, y   -- position of lower-left corner
    width  -- width of rectangle
    height -- height of rectangle
    """
    pass

def _tiled_range(lo, hi, tile_size):
    return range(lo // tile_size, (hi + tile_size - 1) // tile_size) 

def _make_range(x, width, bloat, grid_size):
    return _tiled_range(x + grid_size - 1 - bloat, x + width + bloat, grid_size)

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

    def bounding_box(self, hex):
        """Get the bounding box (as a Rectangle) of a hexagon."""
        width, height = self
        xc, yc = self.center(hex)
        return Rectangle(xc - width, yc - 2*height, 2*width, 4*height)
 
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

    def hexes_in_rectangle(self, rectangle):
        """Return a sequence with the hex coordinates in the rectangle."""
        rx, ry, r_width, r_height = rectangle
        width, height = self
        x_range = _make_range(rx, r_width, width, width)
        y_range = _make_range(ry, r_height, 2*height, 3*height)
        return (Hex(x, y) for y in y_range for x in x_range if (x + y) % 2 == 0)

class HexPathFinder:
    """A* path-finding on the hex grid.
    All positions are represented as Hex objects.

    Important data attributes: 
    found -- True if path-finding is complete and we found a path
    done  -- True if path-finding is complete: we either found a path or know there isn't one
    path  -- The path, as a tuple of positions from start to destination (including both). Empty tuple if found is False.
    """

    found = False
    done = False
    path = None
    
    def __init__(self, start, destination, passable, cost=lambda pos: 1):
        """Create a new HexPathFinder object.
        start       -- Starting position for path finding.
        destination -- Destination position for path finding.
        passable    -- Function of one position, returning True if we can move through this hex.
        cost        -- cost function for moving through a hex. Should return a value ≥ 1. By default all costs are 1.
        """
        self.start = start
        self.destination = destination
        self.passable = passable
        self.cost = cost
        self.closedset = set()
        self.openset = [(self._heuristic(start), 0, start, ())]

    def _heuristic(self, position):
        return self.destination.distance(position)

    def _compute_path(self, path):
        result = []
        while path:
            pos, path = path
            result.append(pos)
        return result[::-1]

    def run_n(self, n):
        """Run at most n path-finding steps.
        This method does a bounded amount of work, and is therefore useful
        if pathfinding must be interleaved with interactive behaviour or may
        be interrupted.
         """
        openset = self.openset
        closedset = self.closedset
        passable = self.passable
        cost = self.cost
        destination = self.destination
        heuristic = self._heuristic

        for i in range(n):
            if not openset:
                self.done = True
                return
            h, cur_cost, pos, path = heappop(openset)
            if pos in closedset:
                continue
            new_path = (pos, path)
            if pos == destination:
                self.path = self._compute_path(new_path)
                self.found = self.done = True
                del openset[:]
                return
            closedset.add(pos)
            for new_pos in pos.neighbours():
                if (not passable(new_pos)) or (new_pos in closedset):
                    continue
                new_cost = cur_cost + cost(new_pos)
                new_h = new_cost + heuristic(new_pos)
                heappush(openset, (new_h, new_cost, new_pos, new_path))

    def run(self):
        """Run path-finding until done, that is, we either found a path or know there isn't one.
        """
        while not self.done:
            self.run_n(100)
