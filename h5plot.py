#!/usr/bin/env python
""" The spiritual successor to ParmDBplot for quickly reviewing gain solutions generated by NDPPP.
"""
import logging
import signal
import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGridLayout, QLabel, \
    QListWidget, QPushButton

from losoto.lib_operations import reorderAxes

import losoto.h5parm as lh5
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.ion()

signal.signal(signal.SIGINT, signal.SIG_DFL)

class H5PlotGUI(QDialog):
    """The main GUI for H5Plot.

    From here the SolSets, SolTabs and antennas to plot are selected.
    """
    def __init__(self, h5file, logging_instance, parent=None):
        super(H5PlotGUI, self).__init__(parent)
        self.logger = logging_instance
        self.figures = []

        self.h5parm = lh5.h5parm(h5file)
        self.solset_labels = self.h5parm.getSolsetNames()
        self.solset = self.h5parm.getSolset('sol000')

        self.soltab_labels = self.solset.getSoltabNames()
        self.soltab = self.solset.getSoltab(self.soltab_labels[0])

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
        self.logger.info('Closing all open figures before exiting.')
        plt.close('all' )
        event.accept()

    def _refant_picker_event(self):
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
        rvals, raxes = reorder_soltab(self.soltab)
        self.stcache.update(rvals, raxes)

    def _phasewrap_event(self):
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
        refantenna = self.refant_picker.currentIndex()
        # Values have shape (timestamps, frequencies, antennas, polarizations, directions).
        values = self.stcache.values[0]
        if (('rotationmeasure' in self.soltab.name) or ('RMextract' in self.soltab.name) or ('clock' in self.soltab.name)) and (self.axis == 'freq'):
            self.logger.warning('Rotation Measure does not support frequency axis! Switch to time instead.')
            return
        else:
            x_axis = self.stcache.values[1][self.axis]
        st_type = self.soltab.getType()
        print(st_type)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(self.stations[antenna])

        if self.axis == 'time':
            if 'rotationmeasure' in self.soltab.name:
                y_axis = values[:, antenna]
                ax.plot(x_axis, y_axis)
            elif ('pol' in self.stcache.axes) and ('dir' in self.stcache.axes):
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[:, 0, antenna, :, 0] - values[:, 0, refantenna, :, 0]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                    y_axis = values[:, antenna]
                else:
                    y_axis = values[:, 0, antenna, :, 0]
                for i in range(y_axis.shape[1]):
                    ax.plot(x_axis, y_axis[:,i], 'h', label=self.stcache.values[1]['pol'][i])
            elif 'pol' in self.stcache.axes:
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[:, 0, antenna, :] - values[:, 0, refantenna, :]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                    y_axis = values[:, antenna]
                else:
                    y_axis = values[:, 0, antenna, :]
                for i in range(y_axis.shape[1]):
                    ax.plot(x_axis, y_axis[:, i], 'h', label=self.stcache.values[1]['pol'][i])
            elif 'dir' in self.stcache.axes:
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[:, 0, antenna, 0] - values[:, 0, refantenna, 0]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                elif (st_type == 'clock') or (st_type == 'rotationmeasure'):
                    y_axis = values[:, antenna]
                else:
                    y_axis = values[:, 0, antenna, 0]
                ax.plot(x_axis, y_axis[:, i], 'h')
            elif ('pol' not in self.stcache.axes) and ('dir' not in self.stcache.axes):
                if (st_type == 'clock') or (st_type == 'rotationmeasure'):
                    y_axis = values[:, antenna]
                else:
                    y_axis = values[:, 0, antenna]
                ax.plot(x_axis, y_axis)
        elif self.axis == 'freq':
            if ('rotationmeasure' in self.soltab.name) or ('clock' in self.soltab.name):
                self.logger.warning('Rotation Measure does not support frequency axis! Switch to time instead.')
            if ('pol' in self.stcache.axes) and ('dir' in self.stcache.axes):
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[0, :, antenna, :, 0] - values[0, :, refantenna, :, 0]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                else:
                    y_axis = values[0, :, antenna, :, 0]
                for i in range(y_axis.shape[1]):
                    ax.plot(x_axis, y_axis[:,i])
            elif 'pol' in self.stcache.axes:
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[0, :, antenna, :] - values[0, :, refantenna, :]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                else:
                    y_axis = values[0, :, antenna, :]
                for i in range(y_axis.shape[1]):
                    ax.plot(x_axis, y_axis[:, i], 'h', label=self.stcache.values[1]['pol'][i])
            elif 'dir' in self.stcache.axes:
                if st_type == 'phase':
                    ax.set_ylim(-np.pi, np.pi)
                    # Plot phase-like quantities w.r.t. to a reference antenna.
                    y_axis = values[0, :, antenna, 0] - values[0, :, refantenna, 0]
                    if self.wrapphase:
                        y_axis = wrap_phase(y_axis)
                else:
                    y_axis = values[0, :, antenna, 0]
            elif ('pol' not in self.stcache.axes) and ('dir' not in self.stcache.axes):
                y_axis = values[0, :, antenna]
                ax.plot(x_axis, y_axis)

        ax.set(xlabel=self.axis, ylabel=labels[1], xlim=limits[0], ylim=limits[1])
        if ax.get_legend_handles_labels()[1]:
            ax.legend()
        self.figures.append(fig)
        fig.show()

class SoltabCache:
    '''Simple class just to store temporarily reordered soltab data.'''
    def __init__(self, values, axes):
        self.values = values
        self.axes = axes

    def update(self, nvalues, naxes):
        self.values = nvalues
        self.axes = naxes

def reorder_soltab(st):
    logging.info('Reordering soltab '+st.name)
    order_old = st.getAxesNames()
    if ('rotationmeasure' in st.name) or ('RMextract'in st.name) or ('clock' in st.name):
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
