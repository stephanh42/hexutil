import unittest
import hexutil

class TestHex(unittest.TestCase):

    def test_is_valid(self):
        self.assertTrue(hexutil.origin.is_valid())
        self.assertTrue(hexutil.Hex(-1, -3).is_valid())
        self.assertFalse(hexutil.Hex(2, -3).is_valid())

    def test_add(self):
        self.assertEqual(hexutil.Hex(2, 3) + hexutil.Hex(4, 5), hexutil.Hex(6, 8))

    def test_sub(self):
        self.assertEqual(hexutil.Hex(2, 3) - hexutil.Hex(4, 6), hexutil.Hex(-2, -3))

    def test_neg(self):
        self.assertEqual(-hexutil.Hex(2, 3), hexutil.Hex(-2, -3))
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


if __name__ == '__main__':
    unittest.main()
