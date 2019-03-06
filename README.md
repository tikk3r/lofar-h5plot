[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/2492)
![pylint Score](https://mperlet.github.io/pybadge/badges/7.29.svg)

**Download from Singularity-hub:** `singularity pull --name h5plot.simg shub://tikk3r/lofar-h5plot`

# LOFAR H5plot
H5plot is a small GUI to view the solutions in an H5parm interactively. To run it directly, clone this repository and run as

    python h5plot.py <h5parm>

or, when using the Singularity image,

    singularity run h5plot.simg <h5parm>

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

A specific Python 2 version will _not_ be released, as it will reach end of life January 1st, 2020. It might work, if the dependencies are there, but your mileage may vary and no official support will be given.
