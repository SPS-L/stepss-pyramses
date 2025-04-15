#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python library for RAMSES dynamic simulator."""

__name__ = "pyramses"
__version__ = '0.0.45'
__author__ = "Petros Aristidou"
__copyright__ = "Petros Aristidou"
__license__ = "Petros Aristidou"
__maintainer__ = "Petros Aristidou"
__email__ = "apetros@pm.me"
__url__ = "https://pyramses.sps-lab.org"
__status__ = "3 - Alpha"

import sys
from warnings import warn

from .cases import cfg
from .globals import __runTimeObs__, __which
from .simulator import sim
from .extractor import extractor, curplot, cur

if sys.platform in ('win32', 'cygwin'):
    checkGnuplot = __which('gnuplot.exe')
else:
    checkGnuplot = __which('gnuplot')
if checkGnuplot is None:
    warn("RAMSES: Gnuplot executable could not be found in the system path, so the runtime observables are disabled.")
    __runTimeObs__ = False
else:
    __runTimeObs__ = True
