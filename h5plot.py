#!/usr/bin/env python3
""" The spiritual successor to ParmDBplot for quickly reviewing gain solutions generated by NDPPP.
"""
import logging
import signal
import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGridLayout, QLabel, \
    QListWidget, QMainWindow, QPushButton, QVBoxLayout
from PyQt5 import QtCore

from losoto.lib_operations import reorderAxes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import losoto.h5parm as lh5
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.ion()

signal.signal(signal.SIGINT, signal.SIG_DFL)

def load_axes(vals, st, axis_type, antenna, refantenna, timeslot=0, freqslot=0):
    """ Load an abscissa and ordinate from the H5Parm.
    
    Args:
        vals (ndarray): raw soltab values to load.
        st_type (str): string describing the type of solutions (e.g. phase, clock, amplitude).
        axis_type (str): `time` or `freq`.
        antenna (str): name of the antenna to select. Automatically determined if set to `None`.
        refant (int): index of the reference antenna.
        timeslot (int): timeslot to load.
        freqslot (int): frequency slot to load.
    Returns:
        xaxis (ndarray): an absicssa to plot.
        yaxis (ndarray): an ordinate to plot.
        plabels (list): a list of labels for each plot (e.g. different polarizations).
        isphase (bool): boolean indicating whether or not the quantity is a phase.

        OR

        errorcode (str): an error message if things went wrong.
    """
    wrapphase = True
    # Values have shape (timestamps, frequencies, antennas, polarizations, directions).
    axes = st.getAxesNames()
    st_type = st.getType()
    x_axis = vals[1][axis_type]
    values = vals[0]
    plabels=[]
    isphase = False
    
    if axis_type == 'time':
        if ('rotationmeasure' in st.name) or ('faraday' in st.name):
            y_axis = values[:, antenna]
            Y_AXIS = y_axis
        elif ('pol' in axes) and ('dir' in axes):
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[:, freqslot, antenna, :, 0] - values[:, freqslot, refantenna, :, 0]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                y_axis = values[:, antenna]
            else:
                y_axis = values[:, freqslot, antenna, :, 0]
            Y_AXIS = []
            plabels = []
            # Iterate over polarizations.
            for i in range(y_axis.shape[1]):
                Y_AXIS.append(y_axis[:,i])
                plabels.append(vals[1]['pol'][i])
        elif 'pol' in axes:
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[:, freqslot, antenna, :] - values[:, freqslot, refantenna, :]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                y_axis = values[:, antenna]
            else:
                y_axis = values[:, freqslot, antenna, :]
            Y_AXIS = []
            plabels = []
            for i in range(y_axis.shape[1]):
                Y_AXIS.append(y_axis[:, i])
                plabels.append(vals[1]['pol'][i])
        elif 'dir' in axes:
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[:, freqslot, antenna, 0] - values[:, freqslot, refantenna, 0]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                y_axis = values[:, antenna]
            else:
                y_axis = values[:, freqslot, antenna, 0]
            Y_AXIS = y_axis[:, i]
        elif ('pol' not in axes) and ('dir' not in axes):
            if (st_type == 'clock') or (st_type == 'rotationmeasure'):
                y_axis = values[:, antenna]
            else:
                y_axis = values[:, freqslot, antenna]
            Y_AXIS = y_axis
    elif axis_type == 'freq':
        if ('rotationmeasure' in st.name) or ('clock' in st.name) or ('faraday' in st.name):
            logging.warning('Rotation Measure does not support frequency axis! Switch to time instead.')
        if ('pol' in axes) and ('dir' in axes):
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[timeslot, :, antenna, :, 0] - values[timeslot, :, refantenna, :, 0]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            else:
                y_axis = values[timeslot, :, antenna, :, 0]
            Y_AXIS = []
            for i in range(y_axis.shape[1]):
                Y_AXIS.append(y_axis[:, i])
        elif 'pol' in axes:
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[timeslot, :, antenna, :] - values[timeslot, :, refantenna, :]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            else:
                y_axis = values[timeslot, :, antenna, :]
            Y_AXIS = []
            plabels=[]
            for i in range(y_axis.shape[1]):
                Y_AXIS.append(y_axis[:, i])
                plabels.append(vals[1]['pol'][i])
        elif 'dir' in axes:
            if st_type == 'phase':
                isphase = True
                # Plot phase-like quantities w.r.t. to a reference antenna.
                y_axis = values[timeslot, :, antenna, 0] - values[timeslot, :, refantenna, 0]
                if wrapphase:
                    y_axis = wrap_phase(y_axis)
            else:
                y_axis = values[timeslot, :, antenna, 0]
            Y_AXIS = y_axis
        elif ('pol' not in axes) and ('dir' not in axes):
            y_axis = values[timeslot, :, antenna]
            Y_AXIS = y_axis
    if len(plabels) == 0:
        plabels = ['', '']
    return x_axis, Y_AXIS, plabels, isphase

class GraphWindow(QDialog):
    """ A window displaying the plotted quantity. Allows the user to cycle through time or frequency.
    """
    def __init__(self, values, frametitle, antindex, refantindex, axis, st, timeslot=0, freqslot=0, times=None, freqs=None, parent=None):
        """ Initialize a new GraphWindow instance.
        
        Args:
            frametitle (str): title the frame will hvae.
            antindex (int): the index of the selected antenna.
            axis (str): the type of axis being plotted (time or freq).
            timeslot (int): index along the time axis to start with.
            freqslot (int): index along the frequency axis to start with.
            parent (QDialog): parent window instance.
        Returns:
            None
        """
        #super(GraphWindow, self).__init__(parent)
        super(GraphWindow, self).__init__()
        # Set up for logging output.
        self.LOGGER = logging.getLogger('GraphWindow')
        #LOGGER.setLevel(logging.INFO)
        self.LOGGER.setLevel(logging.DEBUG)

        self.frametitle = frametitle
        self.axis = axis
        self.timeslot = 0
        self.freqslot = 0
        self.values = values
        self.antindex = antindex
        self.refantindex = refantindex
        self.st = st
        self.parent = parent
        try:
            #self.frequencies = self.parent.frequencies.copy()
            self.frequencies = freqs
        except AttributeError:
            # frequencies is None, plotting against time.
            pass

        try:
            #self.times = self.parent.times.copy()
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
            except:
                # No frequency axis.
                self.select_label = QLabel('')
                self.button_next.setEnabled(False)
                self.button_prev.setEnabled(False)
        elif 'freq' in axis.lower():
            try:
                self.select_label = QLabel('Time: ' + self.format_time(timeslot))
            except:
                # No time axis.
                self.select_label = QLabel('')
                self.button_next.setEnabled(False)
                self.button_prev.setEnabled(False)
        self.select_label.setAlignment(QtCore.Qt.AlignCenter)

        self.buttons = QGridLayout()
        self.buttons.addWidget(self.button_prev, 0, 0)
        self.buttons.addWidget(self.select_label, 0, 1)
        self.buttons.addWidget(self.button_next, 0, 2)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.layout_plot = QVBoxLayout()
        self.layout_plot.addWidget(self.toolbar)
        self.layout_plot.addWidget(self.select_label)
        self.layout_plot.addWidget(self.canvas)

        self.layout = QFormLayout()
        self.layout.addRow(self.layout_plot)
        self.layout.addRow(self.buttons)
        self.setLayout(self.layout)
        
        #self.plot(xaxis, yax, frametitle, limits=[None, None], labels=[labels[0], labels[1]], plot_labels=plot_labels)

    def format_time(self, seconds):
        """ Formats the time to be displayed in the plotting windows.
        
        A string is formatted, displaying the time in seconds or (fractional) minutes or hours.

        Args:
            seconds (int): the time in seconds.
        Returns:
            formatted time (str): formatted time string.
        """
        if seconds < 60:
            return '{:.3f} sec'.format(seconds)
        elif 60 <= seconds < 3600:
            return '{:.3f} min'.format(seconds / 60)
        elif seconds >= 3600:
            return '{:.3f} hr'.format(seconds / 3600)
        else:
            return '{:.3f}'.format(seconds)

    def _forward_button_event(self):
        """ An event triggered by pressing the "Forward" button of a GraphWindow.

        When pressed, the abscissa is advanced one position, showing the next time or frequency slot.
        """
        if 'time' in self.xlabel.lower():
            self.freqslot += 1
            self.select_label.setText('Frequency: {:.3f} MHz'.format(self.frequencies[self.freqslot] / 1e6))
            x, y, l, p = load_axes(self.values, self.st, self.axis, self.antindex, self.refantindex, freqslot = self.freqslot)
            if (self.freqslot > 0) and (not self.button_prev.isEnabled()):
                self.button_prev.setEnabled(True)
            if self.freqslot == (len(self.frequencies) - 1):
                self.button_next.setEnabled(False)
        elif 'freq' in self.xlabel.lower():
            self.timeslot += 1
            self.select_label.setText('Time: ' + self.format_time(self.times[self.timeslot]))
            x, y, l, p = load_axes(self.values, self.st, self.axis, self.antindex, self.refantindex, timeslot = self.timeslot)
            if self.timeslot < (len(self.times) - 1) and (not self.button_prev.isEnabled()):
                self.button_prev.setEnabled(True)
            if self.timeslot == (len(self.times) - 1):
                self.button_next.setEnabled(False)
        self.plot(x, y, self.frametitle, ax_labels=[self.xlabel, self.ylabel], plot_labels=l, isphase=p)

    def _backward_button_event(self):
        """ An event triggered by pressing the "Back" button of a GraphWindow.

        When pressed, the abscissa is set back one position, showing the previous time or frequency slot.
        """
        if 'time' in self.xlabel.lower():
            if self.freqslot > 0:
                self.freqslot -= 1
                self.select_label.setText('Frequency: {:.3f} MHz'.format(self.frequencies[self.freqslot] / 1e6))
                x, y, l, p = load_axes(self.values, self.st, self.axis, self.antindex, self.refantindex, freqslot = self.freqslot)
                if self.freqslot == 0:
                    self.button_prev.setEnabled(False)
                if (self.freqslot < (len(self.frequencies)-1)) and (not self.button_next.isEnabled()):
                    self.button_next.setEnabled(True)
        elif 'freq' in self.xlabel.lower():
            if self.timeslot > 0:
                self.timeslot -= 1
                self.select_label.setText('Time: ' + self.format_time(self.times[self.timeslot]))
                x, y, l, p = load_axes(self.values, self.st, self.axis, self.antindex, self.refantindex, timeslot = self.timeslot)
                if self.timeslot == 0:
                    self.button_prev.setEnabled(False)
                if (self.timeslot < (len(self.parent.times)-1)) and (not self.button_next.isEnabled()):
                    self.button_next.setEnabled(True)
        self.plot(x, y, self.frametitle, ax_labels=[self.xlabel, self.ylabel], plot_labels=l, isphase=p)

    def plot(self, xaxis, yaxis, frametitle='', limits=[None, None], ax_labels=['', ''], plot_labels=[], multidim=False, isphase=False):
        self.xlabel = ax_labels[0]
        self.ylabel = ax_labels[1]
        self.xlabelp = plot_labels[0]
        self.ylabelp = plot_labels[1]
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        self.ax.clear()
        if 'time' in ax_labels[0]:
            # Start counting from t=0
            xaxis = xaxis - xaxis[0]
        self.ax.set_title(frametitle)
        if self.ax.get_legend_handles_labels()[1]:
            self.ax.legend()
        if type(yaxis) is list:
            yaxis = np.asarray(yaxis)
        if len(yaxis.shape) > 1 and len(plot_labels) != 0:
            for i in range(yaxis.shape[0]):
                self.ax.plot(xaxis, yaxis[i, :], '--', alpha=0.25, color='C'+str(i))
                self.ax.plot(xaxis, yaxis[i, :], 'h', label=plot_labels[i], color='C'+str(i))
            self.ax.legend()
        elif len(yaxis.shape) > 1 and len(plot_labels) == 0:
            for i in range(yaxis.shape[0]):
                self.ax.plot(xaxis, yaxis[i, :], '--', alpha=0.25, color='C'+str(i))
                self.ax.plot(xaxis, yaxis[i, :], 'h', color='C'+str(i))
        else:
            self.ax.plot(xaxis, yaxis, '--', alpha=0.25, color='C0')
            self.ax.plot(xaxis, yaxis, 'h', color='C0')
        if isphase:
            self.ax.set_ylim(-np.pi, np.pi)
        self.ax.set(xlabel=ax_labels[0], ylabel=ax_labels[1], xlim=limits[0], ylim=limits[1])
        self.canvas.draw()
        
    

class H5PlotGUI(QDialog):
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
        
        for l in self.soltab_labels:
            try:
                self.frequencies = self.solset.getSoltab(l).getAxisValues('freq')
                break
            except e:
                pass
        for l in self.soltab_labels:
            try:
                self.times = self.solset.getSoltab(l).getAxisValues('time')
                break
            except e:
                pass
        self.stations = self.soltab.getValues()[1]['ant']
        self.refant = 'CS001HBA0'
        self.wrapphase = True

        self.stcache = SoltabCache(self.soltab.getValues(), self.soltab.getAxesNames())
        rvals, raxes = reorder_soltab(self.soltab)
        self.stcache.update(rvals, raxes)

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
        self.axis_picker.addItems(['time', 'freq'])
        self.axis_picker.activated.connect(self._axis_picker_event)
        self.axis = 'time'

        self.refant_label = QLabel('Ref. Ant. ')
        self.refant_picker = QComboBox()
        self.refant_picker.addItems(self.stations)
        self.refant_picker.activated.connect(self._refant_picker_event)

        self.phasewrap_box = QCheckBox('Wrap Phases')
        self.phasewrap_box.setChecked(True)
        self.phasewrap_box.setEnabled(False)
        self.phasewrap_box.stateChanged.connect(self._phasewrap_event)

        self.plot_button = QPushButton('Plot')
        self.plot_button.clicked.connect(self._plot_button_event)

        self.station_picker = QListWidget()
        self.station_picker.addItems(self.stations)
        self.station_picker.setCurrentRow(0)


        plot_layout = QGridLayout()
        plot_layout.addWidget(self.soltab_label_y, 0, 0)
        plot_layout.addWidget(self.soltab_picker, 0, 1)
        plot_layout.addWidget(self.soltab_label_x, 0, 2)
        plot_layout.addWidget(self.axis_picker, 0, 3)
        plot_layout.addWidget(self.refant_label, 1, 0)
        plot_layout.addWidget(self.refant_picker, 1, 1)
        plot_layout.addWidget(self.phasewrap_box, 1, 3)

        layout = QFormLayout(self)
        layout.addRow(self.solset_label, self.solset_picker)
        layout.addRow(plot_layout)
        layout.addRow(self.plot_button)
        layout.addRow(self.station_picker)

    def _axis_picker_event(self):
        """Callback function for when the x-axis is changed.

        Sets the `axis` attribute to the selected axis
        """
        self.logger.debug('Axis changed to: ' + self.axis_picker.currentText())
        self.axis = self.axis_picker.currentText()

    def closeEvent(self, event):
        """ The event triggerd upon closing the main application window.
        """
        self.logger.info('Closing all open figures before exiting.')
        plt.close('all' )
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
        try:
            self.frequencies = self.soltab.getAxisValues('freq')
        except:
            # Soltab probably has no frequency axis.
            pass
        rvals, raxes = reorder_soltab(self.soltab)
        self.stcache.update(rvals, raxes)

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
        self.plot(labels=(self.axis, self.soltab.name))

    
    def plot(self, labels=('x-axis', 'y-axis'), limits=([None, None], [None, None])):
        self.logger.info('Plotting ' + self.soltab.name + ' vs ' + self.axis + \
                         ' for ' + self.solset.name)
        antenna = self.station_picker.currentRow()
        if (('rotationmeasure' in self.soltab.name) or ('RMextract' in self.soltab.name) or ('clock' in self.soltab.name) or ('faraday' in self.soltab.name)) and (self.axis == 'freq'):
            self.logger.info('Rotation Measure or clock does not support frequency axis! Switch to time instead.')
            return
        msg = load_axes(self.stcache.values, self.soltab, self.axis, antenna = antenna, refantenna = int(np.argwhere(self.stations==self.refant)))
        try:
            x_axis, Y_AXIS, plabels, isphase = msg
        except ValueError:
            # Requested combination not supported.
            return
        plot_window = GraphWindow(self.stcache.values, self.stations[antenna], antenna, int(np.argwhere(self.stations==self.refant)), self.axis, self.soltab, times=self.times, freqs=self.frequencies, parent=self)
        #if 'pol' in self.stcache.axes:
        #    plot_window = GraphWindow(self.stations[antenna], antenna, self.axis, times=self.times, freqs=self.frequencies, parent=self)
        #else:
        #    plot_window = GraphWindow(self.stations[antenna], antenna, self.axis, parent=self)
        self.figures.append(plot_window)
        plot_window.plot(x_axis, Y_AXIS, self.stations[antenna], limits=[None, None], ax_labels=[self.axis, labels[1]], plot_labels=plabels, isphase=isphase)
        plot_window.show()

class SoltabCache:
    '''Simple class just to store temporarily reordered soltab data.'''
    def __init__(self, values, axes):
        """ Initialize a new SoltabCache instance.
        
        Args:
            values (ndarray): values to cache.
            axes (ndarray): axes to store.
        Returns:
            None
        """
        self.values = values
        self.axes = axes

    def update(self, nvalues, naxes):
        """ Update the data in the cache.
    
        Args:
            nvalues (ndarray): new values to store in the cache.
            naxes (ndarray): new axes to store in the cache.
        Returns:
            None
        """
        self.values = nvalues
        self.axes = naxes

# Global helper functions.
def reorder_soltab(st):
    """ Reorder a soltab in the order H5plot expects.

    The expected order in the plotter is time, frequency, antenna, polarization, direction.

    Args:
        st (SolTab): soltab instance to reorder the axes of.
    Returns:
        st_new (SolTab): soltab reodered to the expected order.
        order_new (ndarray): array containing the reordered order of the axes.
    """
    logging.info('Reordering soltab '+st.name)
    order_old = st.getAxesNames()
    if ('rotationmeasure' in st.name) or ('RMextract'in st.name) or ('clock' in st.name) or ('faraday' in st.name):
        order_new = ['time', 'ant']
    else:
        order_new = ['time', 'freq', 'ant']
    if 'pol' in order_old:
        order_new += ['pol']
    if 'dir' in order_old:
        order_new += ['dir']
    reordered = reorderAxes(st.getValues()[0], order_old, order_new)
    reordered2 = {}
    for k in order_new:
        reordered2[k] = st.axes[k]
    st.axes = reordered2
    st.axesNames = order_new
    st_new = (reordered, st.getValues()[1])
    return st_new, order_new

def wrap_phase(phase):
    """ Map phases to the range -pi, pi.

    The formula (phase + np.pi) % (2 * np.pi) - np.pi is used to map phases into a plottable range.

    Args:
        phase (ndarray): narray of phases to remap.
    Returns:
        wphase (ndarray): narray of remapped phases.
    """
    wphase = (phase + np.pi) % (2 * np.pi) - np.pi
    return wphase

if __name__ == '__main__':
    FILENAME = sys.argv[1]
    H5FILE = lh5.h5parm(FILENAME, readonly=True)
    # Set up for logging output.
    LOGGER = logging.getLogger('H5plot_logger')
    #LOGGER.setLevel(logging.INFO)
    LOGGER.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOGFILEH = logging.FileHandler('h5plot.log')
    LOGFILEH.setLevel(logging.DEBUG)
    LOGFILEH.setFormatter(formatter)
    LOGGER.addHandler(LOGFILEH)

    LOGGER.info('Successfully opened %s', FILENAME)

    SOLSETS = H5FILE.getSolsetNames()
    print('Found solset(s) '+ ', '.join(SOLSETS))
    for solset in SOLSETS:
        print('SolTabs in ' + solset + ':')
        ss = H5FILE.getSolset(solset)
        soltabs = ss.getSoltabNames()
        print('\t'+', '.join(soltabs))

    # Initialize the GUI.
    APP = QApplication(sys.argv)
    GUI = H5PlotGUI(FILENAME, LOGGER)
    GUI.show()
    APP.exec_()

    H5FILE.close()
    LOGGER.info('%s successfully closed.', FILENAME)
