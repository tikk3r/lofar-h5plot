---
title: Home
layout: home
nav_order: 1
---
Welcome to the home page of [lofar-h5plot]. H5plot is a spiritual successor to the old parmdbplot that allowed users to interactively plot LOFAR calibration solutions. Nowadays those solutions are stored in HDF5 tables. H5plot builds on top of [LoSoTo], which provides various visualisation and manipulation options for these solutions, by providing a GUI to support interactive inspection of the solutions.

# Latest stable version
The latest stable version can be obtained from PyPi via pip:
> pip install lofar-h5plot

For the latest (often experimental) features one can install directly from the master branch via
> pip install git+https://github.com/tikk3r/lofar-h5plot.git

[lofar-h5plot]: https://github.com/tikk3r/lofar-h5plot
[LoSoTo]: https://github.com/revoltek/losoto
