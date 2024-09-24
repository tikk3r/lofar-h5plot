from .widgets import ListWidget
from ..data import reorder_soltab
from ..data.cache import SoltabCache

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6 import QtCore
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QFormLayout, QGridLayout, QLabel, QPushButton, QScrollBar, QHBoxLayout, QVBoxLayout, QWidget

import logging
import losoto.h5parm as lh5
import matplotlib.pyplot as plt
import numpy as np


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

        self.stcache = SoltabCache(self.soltab.getValues(), self.soltab.getAxesNames(), weights=self.soltab.getValues(weight=True)[0])
        rvals, rweights, raxes = reorder_soltab(self.soltab)
        self.stcache.update(rvals, raxes, weights=rweights)

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
        self.soltab_picker.activated.connect(self._soltab_picker_event)
        self.axis_picker = QComboBox()
        self.axis_picker.addItems(['time', 'freq', 'waterfall'])
        self.axis_picker.activated.connect(self._axis_picker_event)
        self.axis = 'time'

        self.refant_label = QLabel('Ref. Ant. ')
        self.refant_picker = QComboBox()
        self.refant_picker.addItems(self.stations)
        self.refant_picker.activated.connect(self._refant_picker_event)

        # self.phasewrap_box = QCheckBox('Wrap Phases')
        # self.phasewrap_box.setChecked(True)
        # self.phasewrap_box.setEnabled(False)
        # self.phasewrap_box.stateChanged.connect(self._phasewrap_event)
        self.dir_label = QLabel('Dir.')
        self.dir_picker = QComboBox()
        self.dir_picker.addItems(self.directions)
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
                zm = np.ma.masked_where(zw == 0, z)
                plot_window.plot(x, y, zm, ax_labels=('Time [s]', 'Freq. [MHz]'), isphase=p, frametitle=self.stations[antenna])
            elif mode == 'weights':
                plot_window.plot(x, y, zw, ax_labels=('Time [s]', 'Freq. [MHz]'), frametitle=self.stations[antenna])

        plot_window.show()


class GraphWindow(QDialog):
    """ A window displaying the plotted quantity. Allows the user to cycle through time or frequency.
    """
    def __init__(self, values, weights, frametitle, antindex, refantindex, axis, st, timeslot=0, freqslot=0, direction=0, times=None, freqs=None, parent=None, mode='values', do_timediff=False, do_freqdiff=False, do_poldiff=False):
        """ Initialize a new GraphWindow instance.

        Args:
            frametitle (str): title the frame will hvae.
            antindex (int): the index of the selected antenna.
            axis (str): the type of axis being plotted (time or freq).
            timeslot (int): index along the time axis to start with.
            freqslot (int): index along the frequency axis to start with.
            direction (str): name of the direction to plot.
            parent (QDialog): parent window instance.
        Returns:
            None
        """
        super(GraphWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowMinMaxButtonsHint | QtCore.Qt.WindowType.WindowCloseButtonHint)
        # Set up for logging output.
        self.LOGGER = logging.getLogger('GraphWindow')
        # LOGGER.setLevel(logging.INFO)
        self.LOGGER.setLevel(logging.DEBUG)

        self.frametitle = frametitle
        self.axis = axis
        self.timeslot = 0
        self.freqslot = 0
        self.direction = direction
        self.values = values
        self.weights = weights
        self.antindex = antindex
        self.refantindex = refantindex
        self.st = st
        self.parent_window = parent
        self.mode = mode
        self.do_timediff = do_timediff
        self.do_freqdiff = do_freqdiff
        self.do_poldiff = do_poldiff
        try:
            self.frequencies = freqs
        except AttributeError:
            # frequencies is None, plotting against time.
            pass

        try:
            self.times = times
            self.times -= self.times[0]
        except AttributeError:
            # times is None, plotting against time.
            pass

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.LOGFILEH = logging.FileHandler('h5plot.log')
        self.LOGFILEH.setLevel(logging.DEBUG)
        self.LOGFILEH.setFormatter(formatter)
        self.LOGGER.addHandler(LOGFILEH)

        self.setWindowTitle(frametitle)

        self.button_next = QPushButton('Forward')
        self.button_next.clicked.connect(self._forward_button_event)
        self.button_prev = QPushButton('Back')
        self.button_prev.clicked.connect(self._backward_button_event)
        self.button_prev.setEnabled(False)
        if 'time' in axis.lower():
            try:
                self.select_label = QLabel('Freq slot {:.2f} MHz'.format(self.frequencies[freqslot] / 1e6))
                if len(self.frequencies == 1):
                    self.button_next.setEnabled(False)
                else:
                    self.button_next.setEnabled(True)
            except TypeError:
                # No frequency axis.
                self.select_label = QLabel('')
                self.button_next.setEnabled(False)
                self.button_prev.setEnabled(False)
        elif 'freq' in axis.lower():
            try:
                self.select_label = QLabel('Time: ' + self.format_time(timeslot))
                if len(self.times == 1):
                    self.button_next.setEnabled(False)
                else:
                    self.button_next.setEnabled(True)
            except TypeError:
                # No time axis.
                self.select_label = QLabel('')
                self.button_next.setEnabled(False)
                self.button_prev.setEnabled(False)
        self.select_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.btn_antiter_next = QPushButton('Next antenna')
        self.btn_antiter_next.clicked.connect(self._antiter_next_button_event)
        self.btn_antiter_prev = QPushButton('Previous antenna')
        self.btn_antiter_prev.clicked.connect(self._antiter_prev_button_event)

        self.btn_diriter_next = QPushButton('Next direction')
        self.btn_diriter_next.clicked.connect(self._diriter_next_button_event)
        self.btn_diriter_prev = QPushButton('Previous direction')
        self.btn_diriter_prev.clicked.connect(self._diriter_prev_button_event)

        antiter_widget = QWidget()
        antiter_layout = QHBoxLayout(antiter_widget)
        antiter_layout.addWidget(self.btn_antiter_prev)
        antiter_layout.addWidget(self.btn_antiter_next)
        antiter_layout.addWidget(self.btn_diriter_prev)
        antiter_layout.addWidget(self.btn_diriter_next)

        self.buttons = QGridLayout()
        self.buttons.addWidget(self.button_prev, 0, 0)
        self.buttons.addWidget(self.select_label, 0, 1)
        self.buttons.addWidget(self.button_next, 0, 2)

        self.scrolls = QGridLayout()
        self.scrollbar = QScrollBar()
        self.scrollbar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        if 'time' in axis.lower() and self.frequencies is not None:
            self.scrollbar.setRange(0, len(self.frequencies)-1)
        elif 'freq' in axis.lower()  and self.times is not None:
            self.scrollbar.setRange(0, len(self.times)-1)
        else:
            self.scrollbar.setDisabled(True)
        self.scrollbar.valueChanged.connect(self._scrollbar_event)
        self.scrolls.addWidget(self.scrollbar, 0, 0)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.window_layout = QVBoxLayout()
        self.window_layout.addWidget(self.toolbar)
        self.window_layout.addWidget(self.canvas, stretch=500)
        self.window_layout.addItem(self.buttons)
        self.window_layout.addItem(self.scrolls)
        self.window_layout.addWidget(antiter_widget)
        self.setLayout(self.window_layout)
