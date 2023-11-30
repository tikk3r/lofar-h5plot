import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel, \
    QLineEdit, QListWidget, QPushButton, QScrollBar, QVBoxLayout, QWidget
from PyQt5 import QtCore, QtWidgets

import numpy as np

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

class H5PlotGUI(QWidget):
    """The main GUI for H5Plot.

    From here the SolSets, SolTabs and antennas to plot are selected.
    """
    def __init__(self, logging_instance, parent=None):
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

        self.move(300, 300)
        self.setWindowTitle('H5Plot')

        self.solset_label = QLabel('SolSet: ')
        self.solset_picker = QComboBox()
        self.solset_picker.activated.connect(self._solset_picker_event)

        self.soltab_label_y = QLabel('Plot ')
        self.soltab_label_x = QLabel(' vs ')
        self.soltab_picker = QComboBox()

        self.soltab_picker.activated.connect(self._soltab_picker_event)
        self.axis_picker = QComboBox()
        self.axis_picker.addItems(['time', 'freq', 'waterfall'])
        self.axis_picker.activated.connect(self._axis_picker_event)
        self.axis = 'time'

        self.refant_label = QLabel('Ref. Ant. ')
        self.refant_picker = QComboBox()
        self.refant_picker.activated.connect(self._refant_picker_event)

        self.dir_label = QLabel('Dir.')
        self.dir_picker = QComboBox()
        self.dir_picker.activated.connect(self._dir_picker_event)

        self.checkbox_layout = QGridLayout()
        self.check_weights = QCheckBox('Plot weights')
        self.check_tdiff = QCheckBox('Time diff.')
        self.check_fdiff = QCheckBox('Freq. diff.')
        self.check_pdiff = QCheckBox('Pol. diff. (XX-YY)')

        self.check_weights.toggled.connect(self._weight_picker_event)
        self.checkbox_layout.addWidget(self.check_weights, 0, 0)
        self.checkbox_layout.addWidget(self.check_tdiff, 0, 1)
        self.checkbox_layout.addWidget(self.check_fdiff, 1, 1)
        self.checkbox_layout.addWidget(self.check_pdiff, 1, 0)

        self.plotmode = 'values'

        self.plot_button = QPushButton('Plot')
        self.plot_button.clicked.connect(self._plot_button_event)

        self.plot_all_button = QPushButton('Plot all stations')
        self.plot_all_button.clicked.connect(self._plot_all_button_event)
        self.plot_all_button.setEnabled(False)

        self.station_picker = ListWidget()
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

    def fill_from_h5parm(self, h5file: str):
        """Load teh given H5parm into the GUI.

        Parameters
        ----------
        h5parm : str
            H5parm to load information from.
        """
        self.h5parm = h5file # lh5.h5parm(h5file)
        self.solset_labels = self.h5parm.getSolsetNames()
        for l in self.solset_labels:
            self.solset_picker.addItem(l)
        self.solset = self.h5parm.getSolset(self.solset_labels[0])

        self.soltab_labels = self.solset.getSoltabNames()
        for l in self.soltab_labels:
            self.soltab_picker.addItem(l)
        self.soltab = self.solset.getSoltab(self.soltab_labels[0])

        for l in self.soltab_labels:
            try:
                self.frequencies = self.solset.getSoltab(l).getAxisValues('freq')
                break
            except TypeError:
                pass
        for l in self.soltab_labels:
            try:
                self.times = self.solset.getSoltab(l).getAxisValues('time')
                break
            except TypeError:
                pass
        for l in self.soltab_labels:
            try:
                if 'pol' in self.solset.getSoltab(l).getAxesNames():
                    self.polarizations = self.solset.getSoltab(l).getAxisValues('pol')
                break
            except TypeError:
                pass
        self.stations = self.soltab.getValues()[1]['ant']
        try:
            self.directions = [s.decode('utf-8') for s in self.solset.getSou().keys()]
        except AttributeError:
            # Probably normal string.
            self.directions = [s for s in self.solset.getSou().keys()]
        self.direction = 0
        self.refant = self.stations[0]
        self.wrapphase = True

        self.refant_picker.addItems(self.stations)
        self.dir_picker.addItems(self.directions)
        self.station_picker.addItems(self.stations)


        # self.stcache = SoltabCache(self.soltab.getValues(), self.soltab.getAxesNames(), weights=self.soltab.getValues(weight=True)[0])
        # rvals, rweights, raxes = reorder_soltab(self.soltab)
        # self.stcache.update(rvals, raxes, weights=rweights)


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
        self.logger.debug('Solset changed to: ' + self.solset_picker.currentText())
        self.solset = self.h5parm.getSolset(self.solset_picker.currentText())
        self.soltab_labels = self.solset.getSoltabNames()
        self.soltab_picker.clear()
        for l in self.soltab_labels:
            self.soltab_picker.addItem(l)
        self._soltab_picker_event()

    def _soltab_picker_event(self):
        """Callback function for when the SolTab is changed.

        Sets the `soltab` attribute.
        """
        self.logger.debug('Soltab changed to: ' + self.soltab_picker.currentText())
        self.soltab = self.solset.getSoltab(self.soltab_picker.currentText())
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

    def plot_waterfall(self, labels=('x-axis', 'y-axis'), mode='values', plot_all=False):
        """ Show a two-dimensional waterfall plot of time vs. frequency.
        """
        if ('phase_offset') in self.soltab.name:
            self.logger.info('Phase-offset is scalar and cannot be plotted in 2D.')
        if (('rotationmeasure' in self.soltab.name) or ('RMextract' in self.soltab.name) or ('clock' in self.soltab.name) or ('faraday' in self.soltab.name) or ('tec' in self.soltab.name)):
            self.logger.info('Rotation Measure, clock, faraday or TEC cannot be plotted in 2D!')
            return
        self.logger.info('Plotting ' + self.soltab.name + \
                         ' for ' + self.solset.name)
        antenna = self.station_picker.currentRow()
        # Data loaded here is xaxis, yaxis, zaxis, isphase
        print('Loading data')
        try:
            #x, y, z, zw, p = msg
            if hasattr(self, "polarizations"):
                if len(self.polarizations) > 1 and self.check_pdiff.isChecked():
                    # Need to plot polarisation difference.
                    x, y, z1, zw1, p = load_axes_2d(self.stcache.values, self.stcache.weights, self.soltab, antenna=antenna, refantenna=int(np.argwhere(self.stations == self.refant)), pol=0, direction=self.direction)
                    x2, y2, z2, zw2, p2 = load_axes_2d(self.stcache.values, self.stcache.weights, self.soltab, antenna=antenna, refantenna=int(np.argwhere(self.stations == self.refant)), pol=-1, direction=self.direction)
                    z = z1 - z2
                    # Combine flags of both polarisations.
                    zw = zw1 * zw2
                else:
                    x, y, z, zw, p = load_axes_2d(self.stcache.values, self.stcache.weights, self.soltab, antenna=antenna, refantenna=int(np.argwhere(self.stations == self.refant)), pol=0, direction=self.direction)
            else:
                x, y, z, zw, p = load_axes_2d(self.stcache.values, self.stcache.weights, self.soltab, antenna=antenna, refantenna=int(np.argwhere(self.stations == self.refant)), pol=0, direction=self.direction)
        except ValueError:
            logging.error('Error loading 2D data!')
            return
        if (len(x) == 1) or (len(y) == 1):
            self.logger.info('Either time or frequency has only 1 entry, not plotting!')
            return
        # print('PLOTTING 2D WEIGHTS')
        try:
            plot_window = GraphWindow2D(self.stcache.values, self.stcache.weights, self.stations[antenna], antenna, int(np.argwhere(self.stations == self.refant)), self.axis, self.soltab, times=self.times, freqs=self.frequencies, pols=self.polarizations, parent=self, direction=self.directions[self.direction], mode=mode, do_timediff=self.check_tdiff.isChecked(), do_freqdiff=self.check_fdiff.isChecked(), do_poldiff=self.check_pdiff.isChecked())
        except AttributeError:
            # No polarizations most likely.
            plot_window = GraphWindow2D(self.stcache.values, self.stcache.weights, self.stations[antenna], antenna, int(np.argwhere(self.stations == self.refant)), self.axis, self.soltab, times=self.times, freqs=self.frequencies, pols=['N/A'], parent=self, direction=self.directions[self.direction], mode=mode, do_timediff=self.check_tdiff.isChecked(), do_freqdiff=self.check_fdiff.isChecked(), do_poldiff=self.check_pdiff.isChecked())
        self.figures.append(plot_window)
        if plot_all:
            plot_window.plot_all()
        else:
            if mode == 'values':
                plot_window.plot(x, y, z, ax_labels=('Time [s]', 'Freq. [MHz]'), isphase=p, frametitle=self.stations[antenna])
            elif mode == 'weights':
                plot_window.plot(x, y, zw, ax_labels=('Time [s]', 'Freq. [MHz]'), frametitle=self.stations[antenna])

        plot_window.show()

    def plot(self, labels=('x-axis', 'y-axis'), limits=([None, None], [None, None]), mode='values', plot_all=False):
        if ('phase_offset') in self.soltab.name:
            self.logger.info('Phase-offset is scalar and cannot be plotted in 2D.')
        self.logger.info('Plotting ' + self.soltab.name + ' vs ' + self.axis + \
                         ' for ' + self.solset.name)
        antenna = self.station_picker.currentRow()
        if (('rotationmeasure' in self.soltab.name) or ('RMextract' in self.soltab.name) or ('clock' in self.soltab.name) or ('faraday' in self.soltab.name) or ('tec' in self.soltab.name)) and (self.axis == 'freq'):
            self.logger.info('Rotation Measure or clock does not support frequency axis! Switch to time instead.')
            return
        msg = load_axes(self.stcache.values, self.soltab, self.axis, antenna=antenna, refantenna=int(np.argwhere(self.stations == self.refant)), direction=self.direction, weights=self.stcache.weights)
        try:
            x_axis, Y_AXIS, Y_AXIS_WEIGHT, plabels, isphase = msg
        except ValueError:
            # Requested combination not supported.
            return
        if 'freq' in self.soltab.getAxesNames():
            plot_window = GraphWindow(self.stcache.values, self.stcache.weights, self.stations[antenna], antenna, int(np.argwhere(self.stations == self.refant)), self.axis, self.soltab, times=self.times, freqs=self.frequencies, parent=self, direction=self.directions[self.direction], mode=mode, do_timediff=self.check_tdiff.isChecked(), do_freqdiff=self.check_fdiff.isChecked(), do_poldiff=self.check_pdiff.isChecked())
        else:
            # Probably TEC or another solution type with no frequency axis.
            plot_window = GraphWindow(self.stcache.values, self.stcache.weights, self.stations[antenna], antenna, int(np.argwhere(self.stations == self.refant)), self.axis, self.soltab, times=self.times, parent=self, direction=self.directions[self.direction], mode=mode, do_timediff=self.check_tdiff.isChecked(), do_freqdiff=self.check_fdiff.isChecked(), do_poldiff=self.check_pdiff.isChecked())
        self.figures.append(plot_window)
        plot_window.plot(x_axis, Y_AXIS, Y_AXIS_WEIGHT, self.stations[antenna], limits=[None, None], ax_labels=[self.axis, labels[1]], plot_labels=plabels, isphase=isphase)
        plot_window.show()

        # TEC does not have a frequency axis, so disable the button as well.
        if 'tec' in self.soltab.name:
            self.logger.debug('TEC solutions detected, disabling buttons.')
            plot_window.button_next.setEnabled(False)
            plot_window.button_prev.setEnabled(False)
        if self.axis.lower() == 'freq' and (len(self.times) == 1):
            plot_window.button_next.setEnabled(False)
            self.logger.debug('Single time slot detected, disabling buttons.')
        elif self.axis.lower() == 'freq' and (len(self.times) > 1):
            self.logger.debug('Multiple time slots detected, enabling buttons.')
            plot_window.button_next.setEnabled(True)
        if self.axis.lower() == 'time' and (self.frequencies is None or (len(self.frequencies) == 1)):
            plot_window.button_next.setEnabled(False)
            self.logger.debug('Single frequency slot detected, disabling buttons.')
        elif self.axis.lower() == 'time' and (len(self.frequencies) > 1):
            self.logger.debug('Multiple frequency slots detected, enabling buttons.')
            plot_window.button_next.setEnabled(True)

def init_gui(logger):
    # Initialize the GUI.
    APP = QApplication(sys.argv)
    GUI = H5PlotGUI(logger)
    GUI.show()
    APP.exec_()

def init_gui_with_h5parm(logger, h5parm: str):
    # Initialize the GUI.
    APP = QApplication(sys.argv)
    GUI = H5PlotGUI(logger)
    GUI.fill_from_h5parm(h5parm)
    GUI.show()
    APP.exec_()
