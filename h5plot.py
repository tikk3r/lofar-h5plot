import logging
import sys

from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QFormLayout, QGridLayout, QLabel, QListWidget, QPushButton, QWidget

import losoto.h5parm as lh5
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

class H5PlotGUI(QDialog):

    def __init__(self, h5file, logger, parent=None):
        super(H5PlotGUI, self).__init__(parent)
        self.logger = logger

        self.h5parm = lh5.h5parm(h5file)
        self.solset_labels = self.h5parm.getSolsetNames()
        self.solset =  self.h5parm.getSolset('sol000')

        self.soltab_labels = self.solset.getSoltabNames()
        self.soltab = self.solset.getSoltab(self.soltab_labels[0])

        self.stations = self.soltab.getValues()[1]['ant']

        self.move(300, 300)
        self.setWindowTitle('H5Plot')

        self.solset_label = QLabel('SolSet: ')
        self.solset_picker = QComboBox()
        for l in self.solset_labels:
            self.solset_picker.addItem(l)
        self.solset_picker.activated.connect(self.solset_picker_event)

        self.soltab_label_y = QLabel('Plot ')
        self.soltab_label_x = QLabel(' vs ')
        self.soltab_picker = QComboBox()
        for l in self.soltab_labels:
            self.soltab_picker.addItem(l)
        self.soltab_picker.activated.connect(self.soltab_picker_event)
        self.axis_picker = QComboBox()
        self.axis_picker.addItems(['time', 'freq'])
        self.axis_picker.activated.connect(self.axis_picker_event)
        self.axis = 'time'

        self.plot_button = QPushButton('Plot')
        self.plot_button.clicked.connect(self.plot_button_event)

        self.station_picker = QListWidget()
        self.station_picker.addItems(self.stations)
        self.station_picker.setCurrentRow(0)


        plot_layout = QGridLayout()
        plot_layout.addWidget(self.soltab_label_y, 0, 0)
        plot_layout.addWidget(self.soltab_picker, 0, 1)
        plot_layout.addWidget(self.soltab_label_x, 0, 2)
        plot_layout.addWidget(self.axis_picker, 0, 3)

        layout = QFormLayout(self)
        layout.addRow(self.solset_label, self.solset_picker)
        layout.addRow(plot_layout)
        layout.addRow(self.plot_button)
        layout.addRow(self.station_picker)

    def axis_picker_event(self):
        self.logger.debug('Axis changed to: ' + self.axis)
        self.axis = self.axis_picker.currentText()

    def solset_picker_event(self):
        self.logger.debug('Solset changed to: ' + self.solset_picker.currentText())
        self.solset = self.h5parm.getSolset(self.solset_picker.currentText())

    def soltab_picker_event(self):
        self.logger.debug('Soltab changed to: ' + self.soltab_picker.currentText())
        self.soltab = self.solset.getSoltab(self.soltab_picker.currentText())

    def plot_button_event(self):
        self.logger.debug('Plotting button pressed.')
        self.plot()

    def plot(self, labels=('x-axis', 'y-axis'), limits=([None,None], [None,None])):
        self.logger.info('Plotting ' + self.soltab.name + ' vs ' + self.axis + ' for ' + self.solset.name)
        fig = plt.figure()
        ax =fig.add_subplot(111)
        antenna = self.station_picker.currentRow()
        print(self.stations[antenna])
        ax.set_title(self.soltab.name + ' vs ' + self.axis + ' for ' + self.stations[antenna] + ' and XX')
        # Values have shape (timestamps, frequencies, antennas, polarizations).
        values = self.soltab.getValues()[0]
        if self.axis == 'time':
            y_axis = [values[:, 0, antenna, pol] for pol in range(values.shape[-1])]
        elif self.axis == 'freq':
            y_axis = [values[0, :, antenna, pol] for pol in range(values.shape[-1])]

        x_axis = self.soltab.getValues()[1][self.axis]
        for i,y in enumerate(y_axis):
            ax.plot(x_axis, y, 'h', label=self.soltab.getValues()[1]['pol'][i])
        ax.set(xlabel=self.axis, ylabel=labels[1], xlim=limits[0], ylim=limits[1])
        ax.legend()
        fig.show()


if __name__ == '__main__':
    filename = sys.argv[1]
    h5file = lh5.h5parm(filename, readonly=True)
    # Set up for logging output.
    logger = logging.getLogger('H5plot_logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logfileH = logging.FileHandler('h5plot.log')
    logfileH.setLevel(logging.DEBUG)
    logfileH.setFormatter(formatter)
    logger.addHandler(logfileH)

    logger.info('Successfully opened '+filename)
    solsets = h5file.getSolsetNames()
    print('Found solset(s) '+ ', '.join(solsets))
    for solset in solsets:
        print('SolTabs in ' + solset + ':')
        ss = h5file.getSolset(solset)
        soltabs = ss.getSoltabNames()
        print('\t', end='')
        print(', '.join(soltabs))

    # Initialize the GUI.
    app = QApplication(sys.argv)
    gui = H5PlotGUI(filename, logger)
    gui.show()
    app.exec_()

    h5file.close()
    logger.info(filename + ' successfully closed.')