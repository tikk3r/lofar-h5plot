"""Module to hold UI related code"""

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPalette, QColor, QColorConstants
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget

from PySide6.QtWidgets import QListWidget


# Now use a palette to switch to dark colors:
class ColourPalette:
    def get_palette_dark(self):
        palette_dark = QPalette()
        palette_dark.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.ColorRole.WindowText, QColorConstants.White)
        palette_dark.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette_dark.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.ColorRole.ToolTipBase, QColorConstants.Black)
        palette_dark.setColor(QPalette.ColorRole.ToolTipText, QColorConstants.White)
        palette_dark.setColor(QPalette.ColorRole.Text, QColorConstants.White)
        palette_dark.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.ColorRole.ButtonText, QColorConstants.White)
        palette_dark.setColor(QPalette.ColorRole.BrightText, QColorConstants.Red)
        palette_dark.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette_dark.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette_dark.setColor(QPalette.ColorRole.HighlightedText, QColorConstants.Black)
        return palette_dark


class ListWidget(QListWidget):
    """Version of QListWidget that resizes itself.

    https://stackoverflow.com/questions/63497841/qlistwidget-does-not-resize-itself
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(-1, -1)

    def viewportSizeHint(self) -> QtCore.QSize:
        if self.model().rowCount() == 0:
            return QtCore.QSize(self.width(), 0)
        height = sum(
            self.sizeHintForRow(i)
            for i in range(self.count())
            if not self.item(i).isHidden()
        )
        width = super().viewportSizeHint().width()
        return QtCore.QSize(width, height)
