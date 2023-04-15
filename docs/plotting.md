---
title: Plotting
layout: default
nav_order: 3
---
# Plotting
This section summarises the various plotting options that are offered.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

# 1D plots
1D plots are your every day x-y plots. It plots the selected quantity versus time or frequency. If multiple polarisations are present they are plotted simultaneously. When solutions are plotted as function of time it is possible to iterate over frequency by means of the "forward" and "backward" buttons, or the scrollbar.

![1D phases]({{ site.baseurl }}/docs/assets/images/plot_1D_phase_freq.png)

![1D amps]({{ site.baseurl }}/docs/assets/images/plot_1D_amp_time.png)

# 2D plots
2D plots, also called "dynamical spectrum" or "waterfall" plots can be made by selecting the "waterfall" option instead of time or frequency. In this case a two-dimensional plot will be generated showing frequency against time where the colour scale indicates the value of the quantity of interest. If multiple polarisations are present, they can be iterated over using the "forward" and "backward" buttons.

![2D phases]({{ site.baseurl }}/docs/assets/images/plot_2D_phase_waterfall.png)

![2D amps]({{ site.baseurl }}/docs/assets/images/plot_2D_amp_waterfall.png)

# Advanced plotting options
A number of options modify the plotting behaviour. These can be useful for more specialised inspections.

## Weights
H5parms have weights associated to their values that indicate whether they are flagged (weight == 0) or not (weight == 1). Ticking the "Plot weights" checkbox will plot these weights instead of the values. This can give a quick indication of which solutions have been flagged.

## Discrete difference
The "Time diff." and/or "Freq. diff." checkboxes will change plotting behaviour such that the first discrete difference is plotted instead of the data itself, plotting `data[i+1] - data[i]` along the respective axes.

## Polarisation difference
The "Pol. diff." checkbox plots the difference between the XX and YY polarisations.