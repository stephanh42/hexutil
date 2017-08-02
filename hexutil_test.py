import unittest
import hexutil

class HexMap(object):
    def __init__(self, str):
        self.source = str
        player = None
        target = None
        tiles = {}
        line_lengths = []
        lights = []
        for y, line in enumerate(str.split("\n")):
            line_lengths.append(len(line))
            for x, ch in enumerate(line):
                if ch.isspace():
                    continue
                position = hexutil.Hex(x, y)
                if ch == '@':
                    player = position
                    ch = '.'
                elif ch == '%':
                    ch = '.'
                elif ch == 'T':
                    target = position
                elif ch == '*':
                    lights.append(position)
                tiles[position] = ch
        self.player = player
        self.target = target
        self.tiles = tiles
        self.line_lengths = line_lengths
        self.lights = lights

    def is_transparent(self, pos):
        return self.tiles.get(pos, '#') != '#'

    def is_passable(self, pos):
        return self.tiles.get(pos, '#') not in "#~"

    def field_of_view(self, max_distance):
        return self.player.field_of_view(transparent=self.is_transparent, max_distance=max_distance)

    def get_map(self, max_distance=None, path=frozenset()):
        if max_distance is not None:
            fov = self.field_of_view(max_distance)
            if self.lights:
                light_fov = {}
                for light in self.lights:
                    light.field_of_view(transparent=self.is_transparent, max_distance=max_distance, visible=light_fov)
            else:
                light_fov = fov
        else:
            fov = light_fov = None
        lines = []
        for y, line_length in enumerate(self.line_lengths):
            line = []
            for x in range(line_length):
                if (x + y) % 2 != 0:
                    ch = ' '
                else:
                    pos = hexutil.Hex(x, y)
                    if pos == self.player:
                        ch = '@'
                    elif fov is None or (fov.get(pos, 0) & light_fov.get(pos, 0)):
                        if pos in path:
                            ch = '%'
                        else:
                            ch = self.tiles.get(pos, ' ')
                    else:
                        ch = ' '
                line.append(ch)
            lines.append("".join(line).rstrip())
        return "\n".join(lines)


testmap1 = HexMap("""
 # # # # # # # # #
# # # # # # # # # #
 # . # # # # # # #
# # . # # # # # # #
 # # # . . . . # #
# # # . @ # # . # #
 # # ~ % . # # . #
# # ~ # % # # # # #
 # # T % # # # # #
# # # # # # # # # #
""")

testmap1_out = """



      # # # #
     # . . .
    # . @ #
   # ~ . . #
  # ~ # . #
   #   . #
      # #
"""

testmap2 = HexMap("""
 # # # # # # # # #
# # # # # # # # # #
 # . # # # * # # #
# # . # # . # # # #
 # # # . % % % # #
# # . . @ # # % # #
 # . # . # # # T #
# # # # . . # # # #
 # # . . . . # # #
# # # # # # # # # #
""")

testmap2_out = """

          # #
           * #
          .
       . . .
      . @
     # . #
      # .


"""


class TestHex(unittest.TestCase):

    def test_is_valid(self):
        hexutil.Hex(-1, -3)
        self.assertRaises(hexutil.InvalidHex, hexutil.Hex, 2, -3)

    def test_rotations(self):
        hex = hexutil.Hex(2, 0)
        self.assertEqual([r(hex) for r in hexutil.Hex.rotations], hexutil.origin.neighbours())

    def test_add(self):
        self.assertEqual(hexutil.Hex(2, 4) + hexutil.Hex(4, 6), hexutil.Hex(6, 10))

    def test_sub(self):
        self.assertEqual(hexutil.Hex(2, 4) - hexutil.Hex(3, 7), hexutil.Hex(-1, -3))

    def test_neg(self):
        self.assertEqual(-hexutil.Hex(2, 4), hexutil.Hex(-2, -4))
        self.assertEqual(-hexutil.origin, hexutil.origin)

    def test_neighbours(self):
        origin = hexutil.origin
        nb = origin.neighbours()
        self.assertEqual(len(nb), 6)
        for h in nb:
            self.assertTrue((-h) in nb)
            self.assertTrue(origin in h.neighbours())

    def test_distance(self):
        h = hexutil.Hex(-1, -3)
        for nb in h.neighbours():
            self.assertEqual(nb.distance(nb), 0)
            self.assertEqual(nb.distance(h), 1)
            self.assertEqual(max(nb2.distance(h) for nb2 in nb.neighbours()), 2)

    def test_rotate_left(self):
        origin = hexutil.origin
        neighbours = origin.neighbours()
        nb = neighbours[0]
        neighbours2 = []
        for i in range(6):
            neighbours2.append(nb)
            nb = nb.rotate_left()
        self.assertEqual(neighbours, neighbours2)

    def test_rotate_right(self):
        origin = hexutil.origin
        for nb in hexutil.origin.neighbours():
            self.assertEqual(nb.rotate_left().rotate_right(), nb)

class TestHexGrid(unittest.TestCase):
    def test_height(self):
        self.assertEqual(hexutil.HexGrid(32).height, 18)

    def test_corners(self):
        self.assertEqual(hexutil.HexGrid(32).corners(hexutil.Hex(1, 1)), 
                 [(64, 72), (32, 90), (0, 72), (0, 36), (32, 18), (64, 36)])

    def test_hex_at_coordinates(self):
        hg = hexutil.HexGrid(32)
        data = [
                ((0, 0), hexutil.Hex(0, 0)),
                ((33, 16), hexutil.Hex(2, 0)),
                ((30, 20), hexutil.Hex(1, 1))
                ]
        for fx in (-1, 1):
            for fy in (-1, 1):
                for pixel, hex in data:
                    x, y = pixel
                    pixel = (fx*x, fy*y)
                    x, y = hex
                    hex = hexutil.Hex(fx*x, fy*y)
                    self.assertEqual(hg.hex_at_coordinate(*pixel), hex, pixel)

    def test_center(self):
        hg = hexutil.HexGrid(32)
        self.assertEqual(hg.center(hexutil.Hex(1, 1)), (32, 54))

    def test_bounding_box(self):
        hg = hexutil.HexGrid(32)
        self.assertEqual(hg.bounding_box(hexutil.Hex(0,2)),
                hexutil.Rectangle(-32, 72, 64, 72))

    def test_hexes_in_rectangle(self):
        hg = hexutil.HexGrid(32)
        self.assertEqual(
                list(hg.hexes_in_rectangle(hg.bounding_box(hexutil.origin))),
                [hexutil.Hex(-1, -1), hexutil.Hex(1, -1),
                 hexutil.Hex(-2, 0), hexutil.Hex(0, 0),
                 hexutil.Hex(-1, 1), hexutil.Hex(1, 1)]
                )

class TestFov(unittest.TestCase):
    def test_fov1(self):
        self.assertEqual(testmap1.get_map(10), testmap1_out)

    def test_fov2(self):
        self.assertEqual(testmap2.get_map(10), testmap2_out)

class TestPathFinding(unittest.TestCase):
    def test_path1(self):
        path = frozenset(testmap1.player.find_path(testmap1.target, testmap1.is_passable)[:-1])
        self.assertEqual(testmap1.get_map(path=path), testmap1.source)

    def test_path2(self):
        path = frozenset(testmap2.player.find_path(testmap2.target, testmap2.is_passable)[:-1])
        self.assertEqual(testmap2.get_map(path=path), testmap2.source)

if __name__ == '__main__':
    unittest.main()
