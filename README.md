<h1 align="center">LOFAR H5plot</h1>
<p align="center">
<img alt="Pylint" src="https://mperlet.github.io/pybadge/badges/8.37.svg?style=for-the-badge">
<img alt="GitHub" src="https://img.shields.io/github/license/tikk3r/lofar-h5plot.svg">
<a href="https://doi.org/10.5281/zenodo.3469995"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3469995.svg" alt="DOI"></a>
<img src="https://img.shields.io/pypi/v/lofar-h5plot">
<img src="https://img.shields.io/pypi/pyversions/lofar-h5plot">
</p>

---

H5plot is a small GUI to view, and optionally flag, the solutions in an H5parm interactively. To run it directly, clone this repository and run as

    python h5plot <h5parm>

This package is also installable through pip:

    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip
    pip install lofar-h5plot

After this, it can simply be run as:

    h5plot <h5parm>

Add `--debug` for more detailed logging. Log messages are also written to `h5plot.log` in the current directory.

![H5plot controls, 1D time and frequency plots, and a waterfall with a marked region](screen.png)

# Usage

## Main window

* **SolSet** and **Plot ... vs ...** select the solution set, the solution table and what to plot it against: `time`, `freq`, or `waterfall` (time against frequency).
* **Ref. Ant.** is the reference antenna for phase-like solutions. By default this is `ST001` if it has unflagged solutions, otherwise the first station that does.
* **Dir.** selects the direction.
* **Plot weights** plots the weights instead of the solutions.
* **Time diff.** and **Freq. diff.** plot the difference between neighbouring time or frequency slots.
* **Pol. diff. (XX-YY)** plots the difference between the first and the last polarization. It is shown for solution tables with two polarizations. **Pol. diff. (XY-YX)** plots the difference between the second and third polarization, and is shown for solution tables with four polarizations.
* **Plot with global values** uses the same colour scale or y-range, given by **Min** and **Max**, for all plots. The defaults are −π to π for phases, the median amplitude divided and multiplied by 2.5 for amplitudes, and the 1st to 99th percentile otherwise.
* **Overwrite input** makes flagging write into the input H5parm instead of a copy, see [Flagging](#flagging).
* Select a station in the list and press **Plot**. For waterfalls, **Plot NxM stations** shows a grid of the given number of rows and columns, starting at the selected station. **Plot all stations** shows all stations at once.

## Plot windows

* All windows have the matplotlib toolbar to zoom, pan and save the figure.
* **Next/Previous antenna** and **Next/Previous direction** step through the stations and directions. In an NxM grid, the antenna buttons go to the next or previous group of stations.
* In plots against time or frequency, **Forward**, **Back** and the scroll bar step through the frequency slots (in plots against time) or time slots (in plots against frequency).
* In waterfalls, **Next/Previous polarization** step through the polarizations, and **Cmap** selects the colour map of phase and amplitude plots. More colour maps are available when the optional [colormaps](https://pratiman-91.github.io/colormaps/) package is installed.
* Flagged solutions are shown in red in plots against time or frequency, and in white in waterfalls.

## Flagging

Solutions can be flagged in plots against time or frequency, in single waterfalls, and in waterfall grids (**Plot NxM stations** and **Plot all stations**).

1. Press **Mark region** (shortcut `A`) and drag a rectangle over the solutions to flag. The rectangle can be moved and resized.
2. To mark more regions, click outside the rectangle. The region is kept, outlined in red, and a new rectangle can be drawn.
3. Press **Flag** to flag all marked regions. **Flag all points** flags the whole plot instead: all points shown in a plot against time or frequency, or the whole waterfall of a single station. It is not available in grids.

Flagging sets the weights of the selected solutions to zero; the solutions themselves are not changed. In plots against time, a region covers the selected times at the frequency slot that is shown; in plots against frequency, the selected frequencies at the time slot that is shown. The **Expand flags** boxes also flag the same region in all **polarizations**, all **directions** or all **antennas**. In plots against time or frequency, unticking **polarizations** flags only the first polarization.

The first time something is flagged, H5plot copies the input to `<input>_flagged.h5` and writes all flags there; it asks before overwriting an existing copy. Copying can take a while for large files. If **Overwrite input** is ticked before the first flag, the flags are written into the input H5parm instead. The flags always go to the solution table of the window they were made in.

Slow steps, such as copying a large H5parm or redrawing a large grid, show a wait cursor and a message at the bottom of the window.

## Applying the flags to a Measurement Set

H5plot keeps track of all flag actions. **Save DP3 parset** in the main window writes them as a DP3 flagging parset, `<h5parm name>_DP3_preflag.parset`, in the directory H5plot was started from. If that file already exists, H5plot asks whether to overwrite it or save under a new name. Apply the flags to the visibilities with

    DP3 <h5parm name>_DP3_preflag.parset msin=<your.ms>

This uses the DP3 preflagger to flag the visibilities of the flagged stations, times and frequencies, and writes the flags into the `FLAG` column of the Measurement Set. Each flag action is listed as a comment in the parset. Note that:

* Visibilities have no directions, so a flag in any direction flags the visibilities of that station, time and frequency range. Flags of the same region in several directions are combined.
* The DP3 preflagger flags all correlations, also when only some polarizations were flagged in the solutions.
* A station flag applies to all baselines with that station. With **Expand flags: antennas**, all baselines are flagged.
* Time and frequency ranges cover the full solution intervals: half a solution interval on either side of the flagged solution times and frequencies.
* The parset contains the flags made since H5plot was started; flags that were already in the H5parm are not included.

H5plot reads the values and weights of the selected solution table into memory. For large H5parms this needs a lot of memory: for example 3600 times × 568 frequencies × 38 stations × 10 directions takes about 12 GB.

# Requirements
* Python >= 3.10
* LoSoTo 2.0
* Matplotlib
* Numpy
* PyQt5, or PySide6 with qtpy on Linux arm64, where PyQt5 has no wheel.
* Optionally [colormaps](https://pratiman-91.github.io/colormaps/) for more colour maps.

These can be installed through

    pip install pyqt5 matplotlib numpy
    pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip

On a minimal Linux installation, Qt may also need system libraries such as OpenGL (`libgl1` on Ubuntu).
