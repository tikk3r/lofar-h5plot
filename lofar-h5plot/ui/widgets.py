""" Module to hold UI related code """
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget

from PySide6.QtWidgets import QListWidget

# Now use a palette to switch to dark colors:
class ColourPalette:
    def get_palette_dark(self):
        palette_dark = QPalette()
        palette_dark.setColor(QPalette.Window, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.WindowText, Qt.white)
        palette_dark.setColor(QPalette.Base, QColor(25, 25, 25))
        palette_dark.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.ToolTipBase, Qt.black)
        palette_dark.setColor(QPalette.ToolTipText, Qt.white)
        palette_dark.setColor(QPalette.Text, Qt.white)
        palette_dark.setColor(QPalette.Button, QColor(53, 53, 53))
        palette_dark.setColor(QPalette.ButtonText, Qt.white)
        palette_dark.setColor(QPalette.BrightText, Qt.red)
        palette_dark.setColor(QPalette.Link, QColor(42, 130, 218))
        palette_dark.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette_dark.setColor(QPalette.HighlightedText, Qt.black)
        return palette_dark

class ListWidget(QListWidget):
    """ Version of QListWidget that resizes itself.
    
    https://stackoverflow.com/questions/63497841/qlistwidget-does-not-resize-itself
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)


    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(-1, -1)


    def viewportSizeHint(self) -> QtCore.QSize:
        if self.model().rowCount() == 0:
            return QtCore.QSize(self.width(), 0)
        height = sum(self.sizeHintForRow(i) for i in range(self.count()) if not self.item(i).isHidden())
        width = super().viewportSizeHint().width()
        return QtCore.QSize(width, height)

