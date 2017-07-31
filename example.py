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


class GameWidget(QtWidgets.QWidget):
    """The Qt Widget which shows the game."""

    _tile_brushes = {
            '.' : QtGui.QBrush(QtGui.QColor("yellow")),
            '#' : QtGui.QBrush(QtGui.QColor("brown")),
            }

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.level = Level(500)
        self.player = hexutil.origin
        self.hexgrid = hexutil.HexGrid(32)
        self.font = QtGui.QFont("Helvetica", 20)
        self.font.setStyleHint(QtGui.QFont.SansSerif)
 
    def paintEvent(self, event):
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        bbox = hexutil.Rectangle(-xc, -yc, size.width(), size.height())
        hexgrid = self.hexgrid
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            pen = QtGui.QPen()
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            painter.setFont(self.font)
            painter.translate(xc, yc)
            for hexagon in hexgrid.hexes_in_rectangle(bbox):
                polygon = QtGui.QPolygon([QtCore.QPoint(*corner) for corner in hexgrid.corners(hexagon)])
                hexagon2 = hexagon + self.player
                tile = self.level.get_tile(hexagon2)
                painter.setBrush(self._tile_brushes[tile])
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
