---
title: Installation
layout: default
nav_order: 2
---

# Installation
{: .no_toc}
## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

This page provides instructions on how to install lofar-h5plot.

---

## Dependencies
The main dependencies of lofar-h5plot are PyQt5, Matplotlib and LoSoTo. On Ubuntu these can be installed through:

> apt-get install qt5-default libgl1-mesa-glx
>
> pip install pyqt5 matplotlib
>
> pip install --upgrade https://github.com/revoltek/losoto/archive/master.zip

## Installation through pip
The easiest way to install lofar-h5plot is through pip. It is made available through PyPi and can be installed through

> pip install lofar-h5plot

## Installation from GitHub
If you are interested in the latest functionality before it appears in an official release, lofar-h5plot can also be installed directly from the master branch through

> pip install git+https://github.com/tikk3r/lofar-h5plot.git