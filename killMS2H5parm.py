#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This tool is used to import killms solutions into a H5parm format.
"""
# Authors:
# Francesco de Gasperin
_author = "Francesco de Gasperin (astro@voo.it)"

import sys, os, glob, pickle
import logging
import numpy as np
from losoto import _version
from losoto import _logging
from losoto import h5parm as h5parm_mod
    
if __name__=='__main__':
    # Options
    import optparse
    opt = optparse.OptionParser(usage='%prog [-v] <H5parm> <killmsfile> \n'\
                    +_author, version='%prog '+_version.__version__)
    opt.add_option('-V', '--verbose', help='Go Vebose! (default=False)', action='store_true', default=False)
    opt.add_option('-s', '--solset', help='Solution-set name (default=sol###)', type='string', default=None)
    opt.add_option('-c', '--complevel', help='Compression level from 0 (no compression, fast) to 9 (max compression, slow) (default=5)', type='int', default='5')
    (options, args) = opt.parse_args()

    # Check options
    if len(args) != 2:
        opt.print_help()
        sys.exit()
    if options.verbose: _logging.setLevel("debug")

    inputFile = args[1]
    logging.info("KILLMS filenames = "+str(inputFile))
    h5parmFile = args[0]
    logging.info("H5parm filename = "+h5parmFile)
    
    # Common options
    complevel = options.complevel
    solsetName = options.solset

    SolsDico = np.load(inputFile)
    Sols = SolsDico["Sols"]
    Sols = Sols.view(np.recarray)

    # build direction subtable
    ClusterCat = SolsDico["ClusterCat"]
    dirCoords = []; dirNames = []
    for i, c in enumerate(ClusterCat):
        dirCoords.append([c[1], c[2]])
        dirNames.append('Dir%02i' % i)

    # build antenna subtable
    stationNames = SolsDico["StationNames"]
    print(stationNames)
    antPos = []; antNames = []
    for i, a in enumerate(stationNames):
        antPos.append([0,0,0])
        antNames.append(a)

    #print SolsDico.keys()
    #print Sols.dtype.names
    pols = ['XX','XY','YX','YY']
    times = (Sols["t0"]+Sols["t1"])/2.
    freqs = (SolsDico['FreqDomains'][:,0]+SolsDico['FreqDomains'][:,1])/2.

    # construct solution arrays
    tt, tf, ta, td, _, _ = Sols['G'].shape
    vals_amp = np.zeros(shape=(4,td,ta,tf,tt))
    vals_ph = np.zeros(shape=(4,td,ta,tf,tt))
    vals_amp[0] = np.abs(Sols['G'][...,0,0].T)
    vals_amp[1] = np.abs(Sols['G'][...,0,1].T)
    vals_amp[2] = np.abs(Sols['G'][...,1,0].T)
    vals_amp[3] = np.abs(Sols['G'][...,1,1].T)
    vals_ph[0] = np.angle(Sols['G'][...,0,0].T)
    vals_ph[1] = np.angle(Sols['G'][...,0,1].T)
    vals_ph[2] = np.angle(Sols['G'][...,1,0].T)
    vals_ph[3] = np.angle(Sols['G'][...,1,1].T)
    #print vals_amp.shape
    #print len(pols), len(dirNames), len(antNames), len(freqs), len(times)

    weights = np.ones(shape=vals_amp.shape)

    is_tec = 'SolsTEC' in list(SolsDico.keys())
    if is_tec:
        # construct TEC array 
        vals_tec = np.zeros(shape=(td,ta,tt))
        vals_tec = SolsDico['SolsTEC'].T
        vals_csp = np.zeros(shape=(td,ta,tt))
        vals_csp = SolsDico['SolsCPhase'].T
        print((vals_tec.shape))
        weights_tec = np.ones(shape=vals_tec.shape)

    # write to h5pram
    h5parm = h5parm_mod.h5parm(h5parmFile, readonly = False, complevel = complevel)
    solset = h5parm.makeSolset(solsetName)
    solset.makeSoltab('amplitude', axesNames=['pol','dir','ant','freq','time'], \
            axesVals=[pols,dirNames,antNames,freqs,times], vals=vals_amp, weights=weights)
    solset.makeSoltab('phase', axesNames=['pol','dir','ant','freq','time'], \
            axesVals=[pols,dirNames,antNames,freqs,times], vals=vals_ph, weights=weights)
    if is_tec:
        solset.makeSoltab('tec', axesNames=['ant','dir','time'], \
                axesVals=[antNames,dirNames,times], vals=vals_tec, weights=weights_tec)
        solset.makeSoltab('phase', 'offset', axesNames=['ant','dir','time'], \
                axesVals=[antNames,dirNames,times], vals=vals_csp, weights=weights_tec)

    # fill source table
    sourceTable = solset.obj._f_get_child('source')
    sourceTable.append(list(zip(*(dirNames,dirCoords))))

    # fill antenna table
    antennaTable = solset.obj._f_get_child('antenna')
    antennaTable.append(list(zip(*(antNames,antPos))))
    print(h5parm)






