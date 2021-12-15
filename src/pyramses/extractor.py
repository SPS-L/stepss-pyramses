#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains the class to extract results simulated with pyramses."""

import warnings
import os
import errno
from scipy.io import FortranFile
from typing import NamedTuple
import numpy as np
import matplotlib.pyplot as plt

from .globals import RAMSESError, CustomWarning, wrapToList

warnings.showwarning = CustomWarning

def curplot(curves):
    """Plots multiple curves

    :param list curves: the curves to plot

    """
    curves = wrapToList(curves)
    for curve in curves:
        plt.plot(curve.time, curve.value, label=curve.msg)
    plt.legend(loc='best',ncol=2)
    plt.xlabel('time (s)')
    plt.show()

class cur(NamedTuple):
    """Class to save results
    """
    time: np.ndarray
    value: np.ndarray
    msg: str

    def plot(self):
        curplot(self)

class extractor(object):
    """The extractor class is used to extract the timeseries data after the simulation and process them. 
    
    :param str rtraj: the path to the ramses trajectory file. This should be the same file that was set in the case with case.addTrj('filenm.rtrj').

    :Example:

    >>> import pyramses
    >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
    >>> ram = pyramses.sim()
    >>> ram.execSim(case) # run the simulation
    >>> ext = pyramses.extractor(case.getTrj())
    >>> ext.getBus('1041').mag.plot() # will plot the timeseries simulated for the voltage magnitude on bus '1041'
    """
    
    def __init__(self,traj):
        if not isinstance(traj, str):
            raise TypeError('PyDyngraph: Class Extractor expects a string path of the trajectory file to initialize.')
        
        self._trajfilename = traj
        
        if not os.path.isfile(traj):
            raise FileNotFoundError(errno.ENOENT, 
                                    os.strerror(errno.ENOENT), traj)    
            
        f = FortranFile(traj, 'r')
        
        self._busnum = f.read_ints()[0]
        self._busname = []
        for i in range(self._busnum):
            self._busname.append(f.read_record(dtype="S18")[0].decode('UTF-8').strip())
        
        self._shunum = f.read_ints()[0]
        self._shuname = []
        for i in range(self._shunum):
            self._shuname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
        
        self._ldnum = f.read_ints()[0]
        self._ldname = []
        for i in range(self._ldnum):
            self._ldname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
        
        self._branum = f.read_ints()[0]
        self._braname = []
        for i in range(self._branum):
            self._braname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
        
        self._syncnum = f.read_ints()[0]
        self._syncname = []
        self._excobsnum = []
        self._excobsname = []
        self._adexc = []
        idxexc = 1
        self._torobsnum = []
        self._torobsname = []
        self._adtor = []
        idxtor = 1
        for i in range(self._syncnum):    
            self._syncname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
            self._excobsnum.append(f.read_ints()[0])
            self._excobsname.append([])
            self._adexc.append(idxexc)
            for j in range(self._excobsnum[i]):
                self._excobsname[i].append(f.read_record(dtype="S10")[0].decode('UTF-8').strip())
            idxexc = idxexc + self._excobsnum[i]
            self._torobsnum.append(f.read_ints()[0])
            self._torobsname.append([])
            self._adtor.append(idxtor)
            for j in range(self._torobsnum[i]):
                self._torobsname[i].append(f.read_record(dtype="S10")[0].decode('UTF-8').strip())
            idxtor = idxtor + self._torobsnum[i]
        self._adexc.append(idxexc)
        self._adtor.append(idxtor)
        
        self._injnum = f.read_ints()[0]
        self._injobsnum = []
        self._injobsname = []
        self._injname = []
        self._adinj = []
        idxinj = 1
        for i in range(self._injnum):
            self._adinj.append(idxinj)
            self._injname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
            self._injobsnum.append(f.read_ints()[0])
            self._injobsname.append([])
            for j in range(self._injobsnum[i]):
                self._injobsname[i].append(f.read_record(dtype="S10")[0].decode('UTF-8').strip())
            idxinj = idxinj + self._injobsnum[i]
        self._adinj.append(idxinj)
        
        self._twopnum = f.read_ints()[0]
        self._twopobsnum = []
        self._twopobsname = []
        self._twopname = []
        self._adtwop = []
        idxtwop = 1
        for i in range(self._twopnum):
            self._adtwop.append(idxtwop)
            self._twopname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
            self._twopobsnum.append(f.read_ints()[0])
            self._twopobsname.append([])
            for j in range(self._twopobsnum[i]):
                self._twopobsname[i].append(f.read_record(dtype="S10")[0].decode('UTF-8').strip())
            idxtwop = idxtwop + self._twopobsnum[i]
        self._adtwop.append(idxtwop)
        
        self._dctlnum = f.read_ints()[0]
        self._dctlobsnum = []
        self._dctlobsname = []
        self._dctlname = []
        self._addctl = []
        idxdctl = 1
        for i in range(self._dctlnum):
            self._addctl.append(idxdctl)
            self._dctlname.append(f.read_record(dtype="S20")[0].decode('UTF-8').strip())
            self._dctlobsnum.append(f.read_ints()[0])
            self._dctlobsname.append([])
            for j in range(self._dctlobsnum[i]):
                self._dctlobsname[i].append(f.read_record(dtype="S10")[0].decode('UTF-8').strip())
            idxdctl = idxdctl + self._dctlobsnum[i]
        self._addctl.append(idxdctl)
        
        self._totobs = 2*self._busnum + self._shunum + 2*self._ldnum + 6*self._branum + \
                       13*self._syncnum + sum(self._excobsnum) + sum(self._torobsnum) + \
                       sum(self._injobsnum) + sum(self._twopobsnum) + sum(self._dctlobsnum)
        
        self._results = []
        buffsz = f.read_ints(np.int64)[0]
        while buffsz > 0:
            temp = f.read_reals(dtype=np.float64)
            self._results = np.concatenate((self._results, temp))
            buffsz = f.read_ints(np.int64)[0]
        
        self._results = np.reshape(self._results, (-1,self._totobs+1), order='C')
        
        self._time = self._results[:,0]
        f.close()
 
    def __del__(self):
        warnings.warn("Extractor of file %s was deleted." % self._trajfilename)
    
    def getBus(self, busname):
        """Returns an object that allows to extract or plot bus related variables.
        
        :param str busname: the name of the bus

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getBus('1041').mag.plot() # will plot the timeseries simulated for the voltage magnitude on bus '1041' 
        
        .. note:: Available data are
           obsnames = ['mag','pha']
           obsdesc = ['Voltage magnitude (pu)','Voltage phase angle (deg)']
        """
        try:
            i=self._busname.index(busname) + 1 # +1 is to go to Fortran notation
            return self._getBusClass(self._time, self._results, 2*(i-1), busname)
        except ValueError:
            warnings.warn('Bus %s not found' % (busname))
    class _getBusClass(object):
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        def __init__(self, time, results, shift, busname):
            self._time = time
            self._results = results
            self._shift = shift
            
            j=0
            self._obsnames = ['mag','pha']
            self._obsdesc = ['Voltage magnitude (pu)','Voltage phase angle (deg)']
            self.obsdict = dict(zip(self._obsnames, self._obsdesc))
            for name,msg in zip(self._obsnames, self._obsdesc):
                j=j+1
                setattr(self, name, self._getElem(j,busname+': '+msg))
                
    def getShunt(self, shuname):
        """Returns an object that allows to extract or plot shunt related variables.
        
        :param str shuname: the name of the shunt

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getShunt('sh1').Q.plot() # will plot the timeseries simulated for the reactive power of shunt 'sh1' 
        
        .. note:: Available data are
           obsnames = ['Q']
           obsdesc = ['Reactive power produced (Mvar)']
        
        """
        try:
            i=self._shuname.index(shuname) + 1 # +1 is to go to Fortran notation
            return self._getShuClass(self._time, self._results, 2*self._busnum + i-1, shuname)
        except ValueError:
            warnings.warn('Shunt %s not found' % (shuname))
            
    class _getShuClass(object):
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        def __init__(self, time, results, shift, shuname):
            self._time = time
            self._results = results
            self._shift = shift     
            j=0
            self._obsnames = ['Q']
            self._obsdesc = ['Reactive power produced (Mvar)']
            self.obsdict = dict(zip(self._obsnames, self._obsdesc))
            for name,msg in zip(self._obsnames, self._obsdesc):
                j=j+1
                setattr(self, name, self._getElem(j,shuname+': '+msg))
        
    def getLoad(self, ldname):
        """Returns an object that allows to extract or plot load related variables.
        
        :param str ldname: the name of the load

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getLoad('L_1').P.plot() # will plot the timeseries simulated for the active power of 'L_1' 
        
        .. note:: Available data are
           obsnames = ['P','Q']
           obsdesc = ['Active power consumed (MW)','Reactive power consumed (Mvar)']
        """
        try:
            i=self._ldname.index(ldname) + 1 # +1 is to go to Fortran notation
            return self._getLdClass(self._time, self._results, 2*self._busnum+self._shunum +2*(i-1), ldname)
        except ValueError:
            warnings.warn('Load %s not found' % (ldname))
            
    class _getLdClass(object):
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        def __init__(self, time, results, shift, ldname):
            self._time = time
            self._results = results
            self._shift = shift
            j=0
            self._obsnames = ['P','Q']
            self._obsdesc = ['Active power consumed (MW)','Reactive power consumed (Mvar)']
            self.obsdict = dict(zip(self._obsnames, self._obsdesc))
            for name,msg in zip(self._obsnames, self._obsdesc):
                j=j+1
                setattr(self, name, self._getElem(j,ldname+': '+msg))
  
    def getBranch(self, braname):
        """Returns an object that allows to extract or plot branch related variables.
        
        :param str braname: the name of the branch

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getBranch('1041-4041').PF.plot() # will plot the timeseries simulated for the active power of line'1041-4041' 
        
        .. note:: Available data are
           obsnames = ['PF','QF','PT','QT','RM','RA']
           obsdesc = ['P (MW) entering at FROM end', 'Q (Mvar) entering at FROM end',
                    'P (MW) entering at TO end', 'Q (Mvar) entering at TO end',
                    'magnitude of transformer ratio','phase angle of transformer ratio (deg)']
        
        """
        try:
            i=self._braname.index(braname) + 1 # +1 is to go to Fortran notation
            return self._getBraClass(self._time, self._results, 2*self._busnum+
                                 self._shunum+2*self._ldnum+6*(i-1), braname)
        except ValueError:
            warnings.warn('Branch %s not found' % (ldnabranameme))
            
    class _getBraClass(object):
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        def __init__(self, time, results, shift, braname):
            self._time = time
            self._results = results
            self._shift = shift
            j=0
            self._obsnames = ['PF','QF','PT','QT','RM','RA']
            self._obsdesc = ['P (MW) entering at FROM end', 'Q (Mvar) entering at FROM end',
                    'P (MW) entering at TO end', 'Q (Mvar) entering at TO end',
                    'magnitude of transformer ratio','phase angle of transformer ratio (deg)']
            self.obsdict = dict(zip(self._obsnames, self._obsdesc))
            for name,msg in zip(self._obsnames, self._obsdesc):
                j=j+1
                setattr(self, name, self._getElem(j,braname+': '+msg))
        
    def getSync(self, syncname):
        """Returns an object that allows to extract or plot synchronous machine related variables.
        
        :param str syncname: the name of the sync machine

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getSync('g1').P.plot() # will plot the timeseries simulated for the active power of 'g1' 
        
        .. note:: 

           Available data are
           * obsnames = ['P','Q','A','S','FW','DD','QD','QW','FC','FV','T','ET','SC']
           * obsdesc = ['active power produced (MW)',
                    'reactive power produced (Mvar)',
                    'rotor angle wrt COI (deg)',
                    'rotor speed (pu)',
                    'flux in field winding (pu mach. base)     ',
                    'flux in d1 damper (pu mach. base)         ',
                    'flux in q1 damper (pu mach. base)         ',
                    'flux in q2 winding (pu mach. base)        ',
                    'field current (pu)                        ',
                    'field voltage (pu)                        ',
                    'mechanical torque (pu)                    ',
                    'electromagnetic torque (pu mach. base)    ',
                    'speed of COI reference (pu)               ']
        """
        try:
            i=self._syncname.index(syncname) + 1 # +1 is to go to Fortran notation
            return self._getSyncClass(self._time, self._results, 
                                  2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                  13*(i-1)+self._adexc[i-1]-1+self._adtor[i-1]-1, syncname)
        except ValueError:
            warnings.warn('Sync machine %s not found' % (syncname))
        
    class _getSyncClass(object):
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, syncname):
            self._time = time
            self._results = results
            self._shift = shift
            j=0
            self._obsnames = ['P','Q','A','S','FW','DD','QD','QW','FC','FV','T','ET','SC']
            self._obsdesc = ['active power produced (MW)',
                    'reactive power produced (Mvar)',
                    'rotor angle wrt COI (deg)',
                    'rotor speed (pu)',
                    'flux in field winding (pu mach. base)     ',
                    'flux in d1 damper (pu mach. base)         ',
                    'flux in q1 damper (pu mach. base)         ',
                    'flux in q2 winding (pu mach. base)        ',
                    'field current (pu)                        ',
                    'field voltage (pu)                        ',
                    'mechanical torque (pu)                    ',
                    'electromagnetic torque (pu mach. base)    ',
                    'speed of COI reference (pu)               ']
            self.obsdict = dict(zip(self._obsnames, self._obsdesc))
            for name,msg in zip(self._obsnames, self._obsdesc):
                j=j+1
                setattr(self, name, self._getElem(j,syncname+': '+msg))
        
    def getExc(self, syncname):
        """Returns an object that allows to extract or plot exciter related variables.
        
        :param str syncname: the name of the generator that we want to check the exciter

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getExc('g1').vf.plot() # will plot the timeseries simulated for the field voltage of 'g1' 
        """
        try:
            i=self._syncname.index(syncname) + 1 # +1 is to go to Fortran notation
            return self._getExcClass(self._time, self._results, 
                                  2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                  13*(i-1)+self._adexc[i-1]-1+self._adtor[i-1]-1 + 13, self._excobsname[i-1], syncname)
        except ValueError:
            warnings.warn('Sync machine %s not found' % (syncname))
        
    class _getExcClass(object):
        
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, excobsname, syncname):
            self._time = time
            self._results = results
            self._shift = shift
            self.obsdict = dict(zip(excobsname, ['User model, refer to the manual']*len(excobsname)))
            j=0
            for name in excobsname:
                j=j+1
                setattr(self, name, self._getElem(j,syncname+': '+name))
    
    def getTor(self, syncname):
        """Returns an object that allows to extract or plot governor related variables.
        
        :param str syncname: the name of the generator that we want to check the governor

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getTor('g1').Tm.plot() # will plot the timeseries simulated for the torque of 'g1' 
        """
        try:
            i=self._syncname.index(syncname) + 1 # +1 is to go to Fortran notation
            return self._getTorClass(self._time, self._results, 
                                  2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                  13*(i-1)+self._adexc[i]-1+self._adtor[i-1]-1 + 13, self._torobsname[i-1], syncname)
        except ValueError:
            warnings.warn('Sync machine %s not found' % (syncname))
        
    class _getTorClass(object):
        
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, torobsname, syncname):
            self._time = time
            self._results = results
            self._shift = shift
            self.obsdict = dict(zip(torobsname, ['User model, refer to the manual']*len(torobsname)))
            j=0
            for name in torobsname:
                j=j+1
                setattr(self, name, self._getElem(j,syncname+': '+name))
                
    def getInj(self, injname):
        """Returns an object that allows to extract or plot injector related variables.
        
        :param str injname: the name of the injector

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getInj('pv1').P.plot() # will plot the timeseries simulated for the active power of 'pv1' 
        """
        try:
            i=self._injname.index(injname) + 1 # +1 is to go to Fortran notation
            return self._getInjClass(self._time, self._results, 
                                 2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                 13*(self._syncnum)+self._adexc[self._syncnum]-1+
                                 self._adtor[self._syncnum]-1+self._adinj[i-1]-1, 
                                 self._injobsname[i-1], injname)
        except ValueError:
            warnings.warn('Injector %s not found' % (injname))
        
    class _getInjClass(object):
        
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, injobsname, injname):
            self._time = time
            self._results = results
            self._shift = shift
            self.obsdict = dict(zip(injobsname, ['User model, refer to the manual']*len(injobsname)))
            j=0
            for name in injobsname:
                j=j+1
                setattr(self, name, self._getElem(j,injname+': '+name))
    
    def getTwop(self, twopname):
        """Returns an object that allows to extract or plot twoport related variables.
        
        :param str twopname: the name of the twoport

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getTwop('lcc1').P1.plot() # will plot the timeseries simulated for the power of 'lcc1' 
        """
        try:
            i=self._twopname.index(twopname) + 1 # +1 is to go to Fortran notation
            return self._getTwopClass(self._time, self._results, 
                                 2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                 13*(self._syncnum)+self._adexc[self._syncnum]-1+
                                 self._adtor[self._syncnum]-1+self._adinj[self._injnum]-1+
                                 self._adtwop[i-1]-1, 
                                 self._twopobsname[i-1], twopname)
        except ValueError:
            warnings.warn('Twoport %s not found' % (twopname))
        
    class _getTwopClass(object):
        
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, twopobsname, twopname):
            self._time = time
            self._results = results
            self._shift = shift
            self.obsdict = dict(zip(twopobsname, ['User model, refer to the manual']*len(twopobsname)))
            j=0
            for name in twopobsname:
                j=j+1
                setattr(self, name, self._getElem(j,twopname+': '+name))
    
    def getDctl(self, dctlname):
        """Returns an object that allows to extract or plot dctl related variables.
        
        :param str dctlname: the name of the dctl

        :Example:

        >>> import pyramses
        >>> case = pyramses.cfg("case.rcfg") # load case from a configuration file
        >>> ram = pyramses.sim()
        >>> ram.execSim(case) # run the simulation
        >>> ext = pyramses.extractor(case.getTrj())
        >>> ext.getDctl('agc').g5.plot() # will plot the timeseries simulated for the power of 'g5' 
        """
        try:
            i=self._dctlname.index(dctlname) + 1 # +1 is to go to Fortran notation
            return self._getDCTLClass(self._time, self._results, 
                                 2*self._busnum+self._shunum+2*self._ldnum+6*self._branum+
                                 13*(self._syncnum)+self._adexc[self._syncnum]-1+
                                 self._adtor[self._syncnum]-1+self._adinj[self._injnum]-1+
                                 self._adtwop[self._twopnum]-1+self._addctl[i-1]-1, 
                                 self._dctlobsname[i-1],dctlname)
        except ValueError:
            warnings.warn('DCTL %s not found' % (dctlname))
        
    class _getDCTLClass(object):
        
        def _getElem(self, j, msg):
            tmp = self._shift + j
            return cur(self._time, self._results[:,tmp], msg)
        
        def __init__(self, time, results, shift, dctlobsname, dctlname):
            self._time = time
            self._results = results
            self._shift = shift
            self.obsdict = dict(zip(dctlobsname, ['User model, refer to the manual']*len(dctlobsname)))
            j=0
            for name in dctlobsname:
                j=j+1
                setattr(self, name, self._getElem(j,dctlname+': '+name))