""" Module to hold UI related code """
import losoto.h5parm as lh5

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QWidget

from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGridLayout, QLabel, QListWidget, QPushButton, QWidget

# Now use a palette to switch to dark colors:
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

def try_get_axis(soltab, axis):
    try: 
        return soltab.getAxisValues(axis)
    except TypeError:
        return None

class H5PlotGUI(QWidget):
    """The main GUI for H5Plot.

    From here the SolSets, SolTabs and antennas to plot are selected.
    """
    def __init__(self, h5file, logging_instance, parent=None):
        """ Initialize a new instances of the H5PlotGUI.

        Args:
            h5file (str): name of the H5Parm to open.
            logging_instance (logging): an instance of the logging module to log to.
        Returns:
            None
        """
        super(H5PlotGUI, self).__init__(parent)
        self.logger = logging_instance
        self.figures = []

        self.h5parm = lh5.h5parm(h5file)
        self.solset_labels = self.h5parm.getSolsetNames()
        self.solset = self.h5parm.getSolset(self.solset_labels[0])

        self.soltab_labels = self.solset.getSoltabNames()
        self.soltab = self.solset.getSoltab(self.soltab_labels[0])

        self.frequencies = try_get_axis(self.soltab, "freq")
        self.times = try_get_axis(self.soltab, "time")
        self.stations = self.soltab.getValues()[1]['ant']
        if 'pol' in self.soltab.getAxesNames():
            self.frequencies = try_get_axis(self.soltab, "pol")
        try:
            self.directions = [s.decode('utf-8') for s in self.solset.getSou().keys()]
        except AttributeError:
            # Probably normal string.
            self.directions = [s for s in self.solset.getSou().keys()]
        self.direction = 0
        self.refant = self.stations[0]
        self.wrapphase = True

        #self.stcache = SoltabCache(self.soltab.getValues(), self.soltab.getAxesNames(), weights=self.soltab.getValues(weight=True)[0])
        #rvals, rweights, raxes = reorder_soltab(self.soltab)
        #self.stcache.update(rvals, raxes, weights=rweights)

        self.move(300, 300)
        self.setWindowTitle('H5Plot')

        self.solset_label = QLabel('SolSet: ')
        self.solset_picker = QComboBox()
        for l in self.solset_labels:
            self.solset_picker.addItem(l)
        #self.solset_picker.activated.connect(self._solset_picker_event)

        self.soltab_label_y = QLabel('Plot ')
        self.soltab_label_x = QLabel(' vs ')
        self.soltab_picker = QComboBox()
        for l in self.soltab_labels:
            self.soltab_picker.addItem(l)
        #self.soltab_picker.activated.connect(self._soltab_picker_event)
        self.axis_picker = QComboBox()
        self.axis_picker.addItems(['time', 'freq', 'waterfall'])
        #self.axis_picker.activated.connect(self._axis_picker_event)
        self.axis = 'time'

        self.refant_label = QLabel('Ref. Ant. ')
        self.refant_picker = QComboBox()
        self.refant_picker.addItems(self.stations)
        #self.refant_picker.activated.connect(self._refant_picker_event)

        # self.phasewrap_box = QCheckBox('Wrap Phases')
        # self.phasewrap_box.setChecked(True)
        # self.phasewrap_box.setEnabled(False)
        # self.phasewrap_box.stateChanged.connect(self._phasewrap_event)
        self.dir_label = QLabel('Dir.')
        self.dir_picker = QComboBox()
        self.dir_picker.addItems(self.directions)
        #self.dir_picker.activated.connect(self._dir_picker_event)

        self.checkbox_layout = QGridLayout()
        self.check_weights = QCheckBox('Plot weights')
        self.check_tdiff = QCheckBox('Time diff.')
        self.check_fdiff = QCheckBox('Freq. diff.')
        self.check_pdiff = QCheckBox('Pol. diff. (XX-YY)')

        #self.check_weights.toggled.connect(self._weight_picker_event)
        self.checkbox_layout.addWidget(self.check_weights, 0, 0)
        self.checkbox_layout.addWidget(self.check_tdiff, 0, 1)
        self.checkbox_layout.addWidget(self.check_fdiff, 1, 1)
        self.checkbox_layout.addWidget(self.check_pdiff, 1, 0)

        self.plotmode = 'values'

        self.plot_button = QPushButton('Plot')
        #self.plot_button.clicked.connect(self._plot_button_event)

        self.plot_all_button = QPushButton('Plot all stations')
        #self.plot_all_button.clicked.connect(self._plot_all_button_event)
        self.plot_all_button.setEnabled(False)

        self.station_picker = ListWidget()
        self.station_picker.addItems(self.stations)
        self.station_picker.setCurrentRow(0)

        plot_layout = QGridLayout()
        plot_layout.addWidget(self.soltab_label_y, 0, 0)
        plot_layout.addWidget(self.soltab_picker, 0, 1)
        plot_layout.addWidget(self.soltab_label_x, 0, 2)
        plot_layout.addWidget(self.axis_picker, 0, 3)
        plot_layout.addWidget(self.refant_label, 1, 0)
        plot_layout.addWidget(self.refant_picker, 1, 1)
        plot_layout.addWidget(self.dir_label, 1, 2,)
        plot_layout.addWidget(self.dir_picker, 1, 3)

        layout = QFormLayout(self)
        layout.addRow(self.solset_label, self.solset_picker)
        layout.addRow(plot_layout)
        layout.addRow(self.checkbox_layout)
        layout.addRow(self.plot_button)
        layout.addRow(self.plot_all_button)
        layout.addRow(self.station_picker)

