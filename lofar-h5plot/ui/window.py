from .widgets import ListWidget

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGridLayout, QLabel, QPushButton, QWidget

import losoto.h5parm as lh5
import matplotlib.pyplot as plt


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
        self.solset_picker.activated.connect(self._solset_picker_event)

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

    def _axis_picker_event(self):
        """Callback function for when the x-axis is changed.

        Sets the `axis` attribute to the selected axis
        """
        self.logger.debug('Axis changed to: ' + self.axis_picker.currentText())
        self.axis = self.axis_picker.currentText()
        if self.axis != 'waterfall':
            self.plot_all_button.setEnabled(False)
        else:
            self.plot_all_button.setEnabled(True)

    def closeEvent(self, event):
        """ The event triggerd upon closing the main application window.
        """
        self.logger.info('Closing all open figures before exiting.')
        plt.close('all')
        for f in self.figures:
            f.close()
        event.accept()

    def _refant_picker_event(self):
        """ An even triggered when a new reference antenna is selected.

        Sets the `refant` attribute.
        """
        self.logger.debug('Reference antenna changed to: ' + self.refant_picker.currentText())
        self.refant = self.refant_picker.currentText()

    def _solset_picker_event(self):
        """Callback function for when the SolSet is changed.

        Sets the `solset` attribute.
        """
        solset_prev = self.solset.name
        self.solset = self.h5parm.getSolset(self.solset_picker.currentText())
        if self.solset.name == solset_prev:
            self.logger.debug("Solset unchanged, not reordering")
            return
        self.logger.debug('Solset changed to: ' + self.solset_picker.currentText())
        self.soltab_labels = self.solset.getSoltabNames()
        self.soltab_picker.clear()
        for l in self.soltab_labels:
            self.soltab_picker.addItem(l)
        self._soltab_picker_event()

    def _soltab_picker_event(self):
        """Callback function for when the SolTab is changed.

        Sets the `soltab` attribute.
        """
        soltab_prev = self.soltab.name
        self.soltab = self.solset.getSoltab(self.soltab_picker.currentText())
        if self.soltab.name == soltab_prev:
            self.logger.debug("Soltab unchanged, not reordering")
            return
        self.logger.debug('Soltab changed to: ' + self.soltab_picker.currentText())
        stations_old = self.stations
        self.stations = self.soltab.getValues()[1]['ant']
        if not np.array_equiv(stations_old, self.stations):
            self.logger.debug('Number of stations changed, updating list.')
            # The list of stations has changed, update the list.
            self.station_picker.clear()
            self.station_picker.addItems(self.stations)
            self.refant_picker.clear()
            self.refant_picker.addItems(self.stations)
        try:
            self.frequencies = self.soltab.getAxisValues('freq')
        except TypeError:
            # Soltab probably has no frequency axis.
            pass
        rvals, rweights, raxes = reorder_soltab(self.soltab)
        self.stcache.update(rvals, raxes, weights=rweights)

    def _dir_picker_event(self):
        """Callback function for when the direction is changed.

        Sets the `direction` attribute.
        """
        self.logger.debug('Direction changed to: ' + self.dir_picker.currentText())
        self.direction = self.dir_picker.currentIndex()

    def _phasewrap_event(self):
        """ An even triggered upon switching phase wrapping on or off. (not yet implemented)
        """
        self.logger.debug('Phase wrapping changed to ' + str(self.phasewrap_box.isChecked()))
        self.wrapphase = self.phasewrap_box.isChecked()

    def _plot_button_event(self):
        """Callback function for when the plot button is pressed.

        Calls the `plot` function subsecquently.
        """
        self.logger.debug('Plotting button pressed.')
        if self.axis == 'freq' or self.axis == 'time':
            self.plot(labels=(self.axis, self.soltab.name), mode=self.plotmode)
        elif self.axis == 'waterfall':
            self.plot_waterfall(labels=('time', 'freq'), mode=self.plotmode)

    def _plot_all_button_event(self):
        """ Callback function for when the plot all stations button is pressed."""
        self.logger.debug('Plotting all stations button pressed.')
        if self.axis == 'freq' or self.axis == 'time':
            self.plot(labels=(self.axis, self.soltab.name), mode=self.plotmode, plot_all=True)
        elif self.axis == 'waterfall':
            self.plot_waterfall(labels=('time', 'freq'), mode=self.plotmode, plot_all=True)

    def _weight_picker_event(self):
        if self.check_weights.isChecked():
            self.plotmode = 'weights'
            self.check_pdiff.setEnabled(False)
            self.check_fdiff.setEnabled(False)
            self.check_tdiff.setEnabled(False)
        else:
            self.plotmode = 'values'
            self.check_pdiff.setEnabled(True)
            self.check_fdiff.setEnabled(True)
            self.check_tdiff.setEnabled(True)
        self.logger.info('Plotting {:s}'.format(self.plotmode))
