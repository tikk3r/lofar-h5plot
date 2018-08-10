[![Build Status](https://travis-ci.org/tikk3r/lofar-h5plot.svg?branch=master)](https://travis-ci.org/tikk3r/lofar-h5plot)
![pylint Score](https://mperlet.github.io/pybadge/badges/8.91.svg)

# lofar-h5plot
Inspect an H5Parm with

    python h5plot.py <h5parm>

This tool is mainly developed in Python 3.6.4, but as of https://github.com/tikk3r/lofar-h5plot/commit/31d05e091c6bfe97eb2a0cf61c9ef02e99942ff0, it should work in Python 2 as well (tested with 2.7.14).
# Requirements
* Python >= 3.6.4
* LoSoTo 2.0
* Matplotlib
* Numpy
* PyQt5

These can be installed through

    pip install pyqt5 matplotlib
    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip
