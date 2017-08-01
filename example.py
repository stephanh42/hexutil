"""
Example of using hexutil.
A simple roguelike kernel written in PyQt5.
"""

import random
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import hexutil

class Level(object):
    """Represents a level in the game.
    Currently there is only one.
    """

    def __init__(self, size):
        """Create level with a random walk"""
        tiles = {}
        tile = hexutil.origin 
        for i in range(size):
            tiles[tile] = '.'
            tile = random.choice(tile.neighbours())
        self.tiles = tiles

    def get_tile(self, hexagon):
        return self.tiles.get(hexagon, '#')

    def is_passable(self, hexagon):
        return self.get_tile(hexagon) != '#'


class GameWidget(QtWidgets.QWidget):
    """The Qt Widget which shows the game."""

    _tile_brushes = {
            '.' : QtGui.QBrush(QtGui.QColor("yellow")),
            '#' : QtGui.QBrush(QtGui.QColor("brown")),
            }

    selected_hexagon = None
    selected_path = frozenset()

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.setMouseTracking(True) # we want to receive mouseMoveEvents

        self.level = Level(500)
        self.player = hexutil.origin
        self.hexgrid = hexutil.HexGrid(32)

        # initialize GUI objects needed for painting
        self.font = QtGui.QFont("Helvetica", 20)
        self.font.setStyleHint(QtGui.QFont.SansSerif)
        self.pen = QtGui.QPen()
        self.pen.setWidth(2)
        self.select_brush = QtGui.QBrush(QtGui.QColor(128, 128, 255, 128))

    def hexagon_of_pos(self, pos):
        """Compute the hexagon at the screen position."""
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        return self.player + self.hexgrid.hex_at_coordinate(pos.x() - xc, pos.y() - yc)

    def mouseMoveEvent(self, event):
        hexagon = self.hexagon_of_pos(event.pos())
        if hexagon != self.selected_hexagon:
            self.selected_hexagon = hexagon
            path = self.player.find_path(hexagon, self.level.is_passable)
            if path is None:
                self.selected_path = frozenset()
            else:
                self.selected_path = frozenset(path[1:])
            self.repaint()
 
    def paintEvent(self, event):
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        bbox = hexutil.Rectangle(-xc, -yc, size.width(), size.height())
        hexgrid = self.hexgrid
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            # set up drawing state
            painter.setPen(self.pen)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            painter.setFont(self.font)
            painter.translate(xc, yc)
            # draw each hexagon which is in the window
            for hexagon in hexgrid.hexes_in_rectangle(bbox):
                polygon = QtGui.QPolygon([QtCore.QPoint(*corner) for corner in hexgrid.corners(hexagon)])
                hexagon2 = hexagon + self.player
                tile = self.level.get_tile(hexagon2)
                painter.setBrush(self._tile_brushes[tile])
                painter.drawPolygon(polygon)
                if hexagon in self.selected_path:
                    painter.setBrush(self.select_brush)
                    painter.drawPolygon(polygon)
                if hexagon2 == self.player:
                    rect = hexgrid.bounding_box(hexagon)
                    rect = QtCore.QRectF(*rect) # convert to Qt RectF
                    painter.drawText(rect, QtCore.Qt.AlignCenter, '@')
        finally:
            painter.end()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = GameWidget()
    window.show()
    app.exec_()

main()
