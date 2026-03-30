#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pyramses — Python interface for the RAMSES dynamic power-system simulator.

Public API exported by this package:

- :class:`~pyramses.cases.cfg` — build and manage a simulation case (input/output files).
- :class:`~pyramses.simulator.sim` — load the RAMSES shared library and run simulations.
- :class:`~pyramses.extractor.extractor` — parse Fortran binary trajectory files post-simulation.
- :class:`~pyramses.extractor.cur` — lightweight NamedTuple holding a (time, value, msg) timeseries.
- :func:`~pyramses.extractor.curplot` — plot one or more :class:`cur` objects on a single axes.

Module-level flags set at import time:

- ``__runTimeObs__`` — ``True`` when gnuplot is available on the system PATH and runtime
  observable plots are therefore enabled; ``False`` otherwise.
"""

__name__ = "pyramses"
__version__ = '0.0.70'
__author__ = "Petros Aristidou"
__copyright__ = "Petros Aristidou"
__license__ = "Apache-2.0"
__maintainer__ = "Petros Aristidou"
__email__ = "apetros@pm.me"
__url__ = "https://stepss.sps-lab.org"
__status__ = "3 - Alpha"

import sys
from warnings import warn

from .cases import cfg
from .globals import __runTimeObs__, __which
from .simulator import sim
from .extractor import extractor, curplot, cur

# Detect gnuplot at import time; disable runtime observables if not found.
if sys.platform in ('win32', 'cygwin'):
    checkGnuplot = __which('gnuplot.exe')
else:
    checkGnuplot = __which('gnuplot')
if checkGnuplot is None:
    warn("RAMSES: Gnuplot executable could not be found in the system path, so the runtime observables are disabled.")
    __runTimeObs__ = False
else:
    __runTimeObs__ = True
