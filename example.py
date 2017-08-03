"""
Example of using hexutil.
A simple roguelike kernel written in PyQt5.
"""

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
        for tile in hexutil.origin.random_walk(100):
            tiles[tile] = '~' # add water
        for tile in hexutil.origin.random_walk(size):
            tiles[tile] = '.' # add floor tiles
        self.tiles = tiles
        self.seen_tiles = {}

    def get_tile(self, hexagon):
        return self.tiles.get(hexagon, '#')

    def get_seen_tile(self, hexagon):
        return self.seen_tiles.get(hexagon, ' ')

    def is_passable(self, hexagon):
        return self.get_tile(hexagon) not in '#~'

    def is_transparent(self, hexagon):
        return self.get_tile(hexagon) != '#'
 
    def update_fov(self, fov):
        for hexagon in fov:
            self.seen_tiles[hexagon] = self.get_tile(hexagon)


class GameWidget(QtWidgets.QWidget):
    """The Qt Widget which shows the game."""

    _tile_brushes = {
            '.' : QtGui.QBrush(QtGui.QColor("yellow")),
            '~' : QtGui.QBrush(QtGui.QColor("blue")),
            '#' : QtGui.QBrush(QtGui.QColor("brown")),
            }

    selected_hexagon = None
    selected_path = frozenset()

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.setMouseTracking(True) # we want to receive mouseMoveEvents

        self.level = Level(500)
        self.player = hexutil.origin
        self.hexgrid = hexutil.HexGrid(24)

        # initialize GUI objects needed for painting
        self.font = QtGui.QFont("Helvetica", 20)
        self.font.setStyleHint(QtGui.QFont.SansSerif)
        self.pen = QtGui.QPen()
        self.pen.setWidth(2)
        self.select_brush = QtGui.QBrush(QtGui.QColor(127, 127, 255, 127))
        self.unseen_brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 127))

        self.update_fov()

    def update_fov(self):
        self.fov = self.player.field_of_view(transparent=self.level.is_transparent, max_distance=10)
        self.level.update_fov(self.fov)

    def hexagon_of_pos(self, pos):
        """Compute the hexagon at the screen position."""
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        return self.player + self.hexgrid.hex_at_coordinate(pos.x() - xc, pos.y() - yc)

    def mousePressEvent(self, event):
        hexagon = self.hexagon_of_pos(event.pos())
        path = self.player.find_path(hexagon, self.level.is_passable)
        if path and len(path) >= 2:
            self.player = path[1]
            self.update_fov()
            self.select_hexagon(event.pos())
            self.repaint()

    def mouseMoveEvent(self, event):
        self.select_hexagon(event.pos())

    def select_hexagon(self, pos):
        """Select hexagon and path to hexagon at position."""
        hexagon = self.hexagon_of_pos(pos)
        if hexagon != self.selected_hexagon:
            self.selected_hexagon = hexagon
            path = self.player.find_path(hexagon, self.level.is_passable)
            if path is None:
                self.selected_path = frozenset()
            else:
                self.selected_path = frozenset(path[1:])
            self.repaint()
 
    def paintEvent(self, event):
        # compute center of window
        size = self.size()
        xc = size.width()//2
        yc = size.height()//2
        # bounding box when we translate the origin to be at the center
        bbox = hexutil.Rectangle(-xc, -yc, size.width(), size.height())
        hexgrid = self.hexgrid
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            # paint background black
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor())
            painter.drawRect(0, 0, size.width(), size.height())
            painter.restore()

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
                tile = self.level.get_seen_tile(hexagon2)
                if tile == ' ':
                    continue
                painter.setBrush(self._tile_brushes[tile])
                painter.drawPolygon(polygon)
                if hexagon2 not in self.fov:
                    painter.setBrush(self.unseen_brush)
                    painter.drawPolygon(polygon)
                if hexagon2 in self.selected_path:
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
