[![Build Status](https://travis-ci.org/tikk3r/lofar-h5plot.svg?branch=master)](https://travis-ci.org/tikk3r/lofar-h5plot)
![pylint Score](https://mperlet.github.io/pybadge/badges/8.85.svg)

# lofar-h5plot
Inspect an H5Parm with

    python h5plot.py <h5parm>

This tool is mainly developed in Python 3.6.4, as it uses PyQt5 at the moment, but a Python 2 version is being worked on.
# Requirements
* Python >= 3.6.4
* LoSoTo 2.0
* Matplotlib
* Numpy
* PyQt5

These can be installed through

    pip install pyqt5 matplotlib
    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip
