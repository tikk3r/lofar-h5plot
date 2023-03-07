<h1 align="center">LOFAR H5plot</h1>
<p align="center">
<img alt="Pylint" src="https://mperlet.github.io/pybadge/badges/8.37.svg?style=for-the-badge">
<img alt="GitHub" src="https://img.shields.io/github/license/tikk3r/lofar-h5plot.svg">
<img alt="Requires.io" src="https://img.shields.io/requires/github/tikk3r/lofar-h5plot.svg">
<a href="https://doi.org/10.5281/zenodo.3469995"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3469995.svg" alt="DOI"></a>
<img src="https://img.shields.io/pypi/v/lofar-h5plot">
<img src="https://img.shields.io/pypi/pyversions/lofar-h5plot">
</p>

---

H5plot is a small GUI to view the solutions in an H5parm interactively. To run it directly, clone this repository and run as

    python h5plot <h5parm>

This package is also installable through pip:

    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip
    pip install lofar-h5plot

After this, it can simply be run as:

    h5plot <h5parm>

![Screenshot](https://raw.githubusercontent.com/tikk3r/lofar-h5plot/master/screen.png)

# Requirements
* Python >= 3.6.4
* LoSoTo 2.0
* Matplotlib
* Numpy
* PyQt5

These can be installed on Ubuntu through

    apt-get install qt5-default libgl1-mesa-glx
    pip install pyqt5 matplotlib
    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip
