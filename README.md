<h1 align="center">LOFAR H5plot</h1>
<p align="center">
<img alt="Singularity-Hub" src="https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg" href="https://singularity-hub.org/collections/2492">
<img alt="Pylint" src="https://mperlet.github.io/pybadge/badges/7.29.svg">
<img alt="GitHub" src="https://img.shields.io/github/license/tikk3r/lofar-h5plot.svg">
<img alt="Requires.io" src="https://img.shields.io/requires/github/tikk3r/lofar-h5plot.svg">
</p>
<p align="center">
    <b>Download the latest commit from Singularity-hub:</b><br/>
<tt>singularity pull --name h5plot.simg shub://tikk3r/lofar-h5plot</tt><br/>
The image is always the latest commit on the master branch, no guarantees on stability.
</p>

---

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
