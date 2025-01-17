#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python module for RAMSES dynamic simulator. It provides an interface through Python to
perform dynamic simulations and extract data from RAMSES."""

import ctypes
import _ctypes
import os
import sys
import warnings
import datetime
import numpy as np
from scipy.sparse import coo_matrix

from .cases import cfg
from .globals import RAMSESError, CustomWarning, __libdir__, wrapToList

class sim(object):
    """Simulation class."""

    warnings.showwarning = CustomWarning

    ramsesCount = 0  # Provides a sum of all instances of Ramses running
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # This allows to run even if 2 versions of MKL are present on the computer

    # print(__libdir__)
    # print(os.path.join(__libdir__,"ramses.dll"))

    def __init__(self, custLibDir = None):
        """Initialize the DLL libraries."""
        if custLibDir is None:
            ramLibDir = __libdir__
        else:
            try:
                if os.path.exists(custLibDir) and os.path.isdir(custLibDir):
                    ramLibDir = custLibDir
                    warnings.warn("Overwriting the internal DLL with the one at %s. The DLL in that location will be locked. To unlock it, you need to del() this instance of pyramses.sim() or restart the kernel." % ramLibDir)
                else:
                    raise RAMSESError('RAMSES: The path %s does not exist or it is not a directory.' % (custLibDir))
            except OSError as e:
                raise RAMSESError('RAMSES: The path %s gave an error: ' % (custLibDir), e)
            
        try:
            # print(sys.platform)
            if sys.platform in ('win32', 'cygwin'):
                self._ramseslib = ctypes.CDLL(os.path.join(ramLibDir, "ramses.dll"))
            else:
                # if (not find_library('iomp5')):
                # self._omplib = ctypes.CDLL(os.path.join(__libdir__, "libiomp5.so"), mode=ctypes.RTLD_GLOBAL)
                # self._mkllib = ctypes.CDLL(os.path.join(__libdir__, "libmkl.so"), mode=ctypes.RTLD_GLOBAL)
                self._ramseslib = ctypes.CDLL(os.path.join(ramLibDir, "ramses.so"))
        except OSError as e:
            raise ImportError('RAMSES: ', e)

        sim.ramsesCount += 1
        self._ramsesNum = sim.ramsesCount  # This is the current instance of Ramses
        self._setcalls()

    def __del__(self):
        warnings.warn("Simulator with number %i was deleted." % self._ramsesNum)
        if sys.platform in ('win32', 'cygwin'):
            _ctypes.FreeLibrary(self._ramseslib._handle)
        else:
            _ctypes.dlclose(self._ramseslib._handle)
        sim.ramsesCount -= 1

    def _c_func_wrapper(self, cdecl_text):
        """Read the ramses.h file and sets the necessary call types for Python."""

        def move_pointer_and_strip(type_def, name):
            if '*' in name:
                type_def += ' ' + name[:name.rindex('*') + 1]
                name = name.rsplit('*', 1)[1]
            return type_def.strip(), name.strip()

        def type_lookup(type_def):
            '''Supported C variable types and their ctypes equivalents.'''
            types = {
                'void': None,
                'char *': ctypes.c_char_p,
                'int': ctypes.c_int,
                'int *': ctypes.POINTER(ctypes.c_int),
                'void *': ctypes.c_void_p,
                'size_t': ctypes.c_size_t,
                'size_t *': ctypes.POINTER(ctypes.c_size_t),
                'double': ctypes.c_double,
                'double *': ctypes.POINTER(ctypes.c_double)
            }
            type_def_without_const = type_def.replace('const ', '')
            if type_def_without_const in types:
                return types[type_def_without_const]
            elif (type_def_without_const.endswith('*') and type_def_without_const[:-1] in types):
                return ctypes.POINTER(types[type_def_without_const[:-1]])
            else:
                raise KeyError(type_def)

        a, b = [i.strip() for i in cdecl_text.split('(', 1)]
        params, _ = b.rsplit(')', 1)
        rtn_type, name = move_pointer_and_strip(*a.rsplit(' ', 1))
        param_spec = []
        for param in params.split(','):
            if param != 'void':
                param_spec.append(move_pointer_and_strip(*param.rsplit(' ', 1)))

        try:
            func = getattr(self._ramseslib, name)  # get the function from the dll
            setattr(func, 'restype', type_lookup(rtn_type))  # set the return type
            setattr(func, 'argtypes', [type_lookup(type_def) for type_def, _ in param_spec])  # set the argument types
        except AttributeError as e:
            #raise AttributeError(
            #    'RAMSES: Function %s is listed in ramses.h but cannot be found in the library.' % (name), e)
            warnings.warn('RAMSES: Function %s is listed in ramses.h but cannot be found in the library.' % (name))
            print(e)

    def _setcalls(self):
        """Define the argument types and returning types for the routines in RAMSES"""
        try:
            with open(os.path.join(__libdir__, "ramses.h"), 'r') as f:
                _C_HEADER = f.read()
                for cdecl_text in _C_HEADER.splitlines():
                    if cdecl_text.strip():
                        if not cdecl_text.startswith("//"):
                            self._c_func_wrapper(cdecl_text)
        except IOError as e:
            raise IOError("RAMSES: Cannot open ramses.h files", e)

    def getLastErr(self):
        """Return the last error message issued by RAMSES.

        :rtype: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0) # start simulation paused
        >>> ram.getLastErr()
        'This is an error msg'

        """

        errMsg = ctypes.create_string_buffer(1024)

        try:
            retval = self._ramseslib.get_last_err_log(errMsg)
        except KeyError:
            retval = 1

        if (retval != 0):
            raise RAMSESError('RAMSES: Function getLastErr failed.')

        return errMsg.value.decode()

    def getJac(self):
        """Gets the Jacobian matrix written in files

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0) # start simulation paused
        >>> ram.getJac()

        """
        try:
            retval = self._ramseslib.get_Jac()
        except KeyError:
            retval = 1

        if (retval != 0) and (retval != 112):
            raise RAMSESError('RAMSES: Function get_Jac failed.')
        
        Nmat = 0
        try:
            f = open('py_eqs.dat','r')
            lines = f.readlines()
            f.close()
            rowl = []
            coll = []
            datal = []
            for x in lines:
                xsplit = x.split()
                if int(xsplit[0]) > Nmat:
                    Nmat = int(xsplit[0])
                if int(xsplit[5]) > 0:
                    rowl.append(int(xsplit[0])-1)
                    coll.append(int(xsplit[5])-1)
                    datal.append(1)
            row = np.array( rowl, dtype=int )
            col = np.array( coll, dtype=int )
            data = np.array( datal, dtype=float )
            E = coo_matrix((data,(row,col)), shape=(Nmat,Nmat)).tocsc()
        except:
            raise RAMSESError('RAMSES: Function get_Jac failed while reading E.')
            
        try:
            f = open('py_val.dat','r')
            lines = f.readlines()
            f.close()
            row = np.array( [ int(x.split()[0])-1 for x in lines ], dtype=int )
            col = np.array( [ int(x.split()[1])-1 for x in lines ], dtype=int )
            data = np.array( [ x.split()[2] for x in lines ], dtype=float )
            A = coo_matrix((data,(row,col)), shape=(Nmat,Nmat)).tocsc()
        except:
            raise RAMSESError('RAMSES: Function get_Jac failed while reading A.')

        return A, E

    def getCompName(self, comp_type, num):
        """Return the name of the num:superscript:`th` component of type comp_type.

        :param str comp_type: the component type (BUS, SYNC, INJ, DCTL, BRANCH, TWOP, SHUNT, LOAD)
        :param int num: The number of the component to be fetched
        :returns: The component name
        :rtype: srt

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0) # start simulation paused
        >>> ram.getCompName("BUS",1)
        'B1'

        """
        get_name_func = {
            'BUS': self._ramseslib.get_bus_name,
            'SYNC': self._ramseslib.get_sync_name,
            'INJ': self._ramseslib.get_inj_name,
            'DCTL': self._ramseslib.get_dctl_name,
            'BRANCH': self._ramseslib.get_branch_name,
            'TWOP': self._ramseslib.get_twop_name,
            'SHUNT': self._ramseslib.get_shunt_name,
            'LOAD': self._ramseslib.get_load_name
        }

        name = ctypes.create_string_buffer(21)

        try:
            retval = get_name_func[comp_type](num, name)
        except KeyError:
            retval = 1

        if (retval != 0):
            raise RAMSESError(
                'RAMSES: Function getCompName(%s,%i) failed. Does this component exist?' % (comp_type, num))

        return name.value.decode()

    def getAllCompNames(self, comp_type):
        """Get list of all components of type comp_type

        :param str comp_type: the component type (BUS, SYNC, INJ, DCTL, BRANCH, TWOP, SHUNT, LOAD)
        :returns: list of component names
        :rtype: list of str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0) # start simulation paused
        >>> ram.getAllCompNames("BUS")
        ['B1',
        'B2',
        'B3']

        """
        get_nb_func = {
            'BUS': self._ramseslib.get_nbbus,
            'SYNC': self._ramseslib.get_nbsync,
            'INJ': self._ramseslib.get_nbinj,
            'DCTL': self._ramseslib.get_nbdctl,
            'BRANCH': self._ramseslib.get_nbbra,
            'TWOP': self._ramseslib.get_nbtwop,
            'SHUNT': self._ramseslib.get_nbshunt,
            'LOAD': self._ramseslib.get_nbload
        }

        try:
            Nb = get_nb_func[comp_type]()
        except KeyError:
            raise RAMSESError(
                'RAMSES: Function getAllCompName(%s) failed. Does this component type exists?' % (comp_type))

        names = []
        if Nb > 0:
            for comp in range(1, Nb + 1):
                names.append(self.getCompName(comp_type, comp))
        return names

    def execSim(self, cmd, pause=None):
        """Run a simulation.

        :param cmd: provides the case description
        :type cmd: type(:class:`.cfg`)
        :param t_pause: pause time (optional). If not given, the simulation will run until the end as described in the dst file.
        :type t_pause: float

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case) # start simulation

        .. note:: If you have an existing command file, you can pass it to the simulator as pyramses.cfg("cmd.txt")
        """
        if not isinstance(cmd, cfg):
            raise TypeError('RAMSES: Function execSim because the command file is not of type pyramses.cfg()')
        if pause is not None:
            self.pauseSim(pause)
        cmdfilename = cmd.writeCmdFile()
        if not cmd._out:
            outfilename = os.path.join(os.getcwd(),'output '+datetime.datetime.now().strftime("%d.%m.%Y-%H.%M.%S")+'.trace')
        else:
            outfilename = cmd._out[0]
        retval = self._ramseslib.ramses(cmdfilename.encode('utf-8'), outfilename.encode('utf-8'))
        if (retval != 0) and (retval != 112):
            raise RAMSESError('RAMSES: Function execSim() failed with the flag %i. Last message was: %s' % (retval, self.getLastErr()))
        return 0

    def contSim(self, pause=None):
        """Continue the simulation until the given time.

        The pause argument is optional and it gives the time until the simulation will stop."""
        if pause is not None:
            self.pauseSim(pause)
        retval = self._ramseslib.continue_simul()
        if (retval != 0) and (retval != 112):
            raise RAMSESError('RAMSES: Function contSim() failed with the flag %i. Last message was: %s' % (retval, self.getLastErr()))
        return 0

    def getBusVolt(self, busNames):
        """Return the voltage magnitude of a list of buses

        :param busNames: the names of buses
        :type busNames: list of str
        :returns: list of bus voltage magnitudes
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> buses = ['g1','g2','g3']
        >>> ram.getBusVolt(buses)
        [1.0736851673414456,
         1.0615442362180327,
         1.064702686997689]
        """
        volts = []
        bus_volt = ctypes.c_double()
        for bus in busNames:
            retval = self._ramseslib.get_volt_mag(bus.encode('utf-8'), bus_volt)
            if (retval != 0):
                raise RAMSESError(
                    'RAMSES: Function getBusVolt(%s) failed with the flag %i.  Does the bus exist? Last message was: %s' % (bus, retval, self.getLastErr()))
            volts.append(bus_volt.value)
        return volts

    def getBranchPow(self, branchName):
        """Return the active and reactive powers of a list of branches

        :param branchName: the names of branches
        :type branchName: list of str
        :returns: list of branch powers. These are active and reactive power at the origin and extremity respectively (p_orig, q_orig, p_extr, q_extr)
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> branchName = ['1011-1013','1012-1014','1021-1022']
        >>> ram.getBranchPow(branchName)
        """
        pows = []
        p_orig = ctypes.c_double()
        q_orig = ctypes.c_double()
        p_extr = ctypes.c_double()
        q_extr = ctypes.c_double()
        for branch in branchName:
            retval = self._ramseslib.get_line_pow(branch.encode('utf-8'), p_orig, q_orig, p_extr, q_extr)
            if (retval != 0):
                raise RAMSESError(
                    'RAMSES: Function get_line_pow(%s) failed with the flag %i.  Does the branch exist? Last message was: %s' % (branch, retval, self.getLastErr()))
            thisBranch = [p_orig.value, q_orig.value, p_extr.value, q_extr.value]
            pows.append(thisBranch)
        return pows

    def getBranchCur(self, branchName):
        """Return the currents of a list of branches

        :param branchName: the names of branches
        :type branchName: list of str
        :returns: list of branch currents. These are x-y components at the origin and extremity respectively (ix_orig, iy_orig, ix_extr, iy_extr)
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> branchName = ['1011-1013','1012-1014','1021-1022']
        >>> ram.getBranchCur(branchName)

        """
        curs = []
        ix_orig = ctypes.c_double()
        iy_orig = ctypes.c_double()
        ix_extr = ctypes.c_double()
        iy_extr = ctypes.c_double()
        for branch in branchName:
            retval = self._ramseslib.get_line_cur(branch.encode('utf-8'), ix_orig, iy_orig, ix_extr, iy_extr)
            if (retval != 0):
                raise RAMSESError(
                    'RAMSES: Function get_line_cur(%s) failed with the flag %i.  Does the branch exist? Last message was: %s' % (branch, retval, self.getLastErr()))
            thisBranch = [ix_orig.value, iy_orig.value, ix_extr.value, iy_extr.value]
            curs.append(thisBranch)
        return curs        

    def getBusPha(self, busNames):
        """Return the voltage phase of a list of buses

        :param busNames: the names of buses
        :type busNames: list of str
        :returns: list of bus voltage phase
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> buses = ['g1','g2','g3']
        >>> ram.getBusPha(buses)
        [0.0000000000000000,
         10.0615442362180327,
         11.064702686997689]

        """
        pha = []
        bus_pha = ctypes.c_double()
        for bus in busNames:
            retval = self._ramseslib.get_volt_pha(bus.encode('utf-8'), bus_pha)
            if (retval != 0):
                raise RAMSESError(
                    'RAMSES: Function getBusPha(%s) failed with the flag %i.  Does the bus exist? Last message was: %s' % (bus, retval, self.getLastErr()))
            pha.append(bus_pha.value)
        return pha

    def endSim(self):
        """End the simulation"""

        self._ramseslib.set_end_simul()
        return self.contSim(self.getInfTime())
    
    def getEndSim(self):
        """Check if the simulation has ended
        
        :returns: 0 -> simulation is still working, 1 -> simulation has ended
        :rtype: integer
        
        """

        return self._ramseslib.get_end_simul()

    def getSimTime(self):
        """Get the current simulation time

        :returns: current simulation time in RAMSES.
        :rtype: float

        """
        return self._ramseslib.get_sim_time()

    def getInfTime(self):
        """Get the maximum representable double from the simulator ()

        :returns: maximum representable double
        :rtype: float

        """
        return self._ramseslib.get_huge_double()

    def initObserv(self,traj_filenm):
        """Initialize observable selection (structure and trajectory file)

        :param traj_filenm: the file to save the trajectory at
        :type traj_filenm: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt") # command file without any observables
        >>> ram.execSim(case, 0.0) # start
        >>> traj_filenm = 'obs.trj'
        >>> ram.initObserv(traj_filenm)
        """

        return self._ramseslib.initObserv(traj_filenm.encode('utf-8'))

    def addObserv(self,string):
        """Add an element to be observed

        :param string: the element with proper format
        :type string: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt") # command file without any observables
        >>> ram.execSim(case, 0.0) # start
        >>> traj_filenm = 'obs.trj'
        >>> ram.initObserv(traj_filenm)
        >>> string = 'BUS *' # monitor all buses
        >>> ram.addObserv(string)
        """

        return self._ramseslib.addObserv(string.encode('utf-8'))

    def finalObserv(self):
        """Finalize observable selection, allocate buffer, and write header of trajectory file

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt") # command file without any observables
        >>> ram.execSim(case, 0.0) # start
        >>> traj_filenm = 'obs.trj'
        >>> ram.initObserv(traj_filenm)
        >>> string = 'BUS *' # monitor all buses
        >>> ram.addObserv(string)
        >>> ram.finalObserv()
        """

        return self._ramseslib.finalObserv()

    def getPrm(self, comp_type, comp_name, prm_name):
        """Get the value of a named parameter

        :param comp_type: the types of components (EXC, TOR, INJ, DCTL, TWOP)
        :type comp_type: list of str
        :param comp_name: the names of components
        :type comp_name: list of str
        :param prm_name: the names of parameters
        :type prm_name: list of str

        :returns: list of parameter values
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> comp_type = ['EXC','EXC','EXC']
        >>> comp_name = ['g1','g2','g3']
        >>> prm_name = ['V0','V0','V0']
        >>> ram.getPrm(comp_type,comp_name, prm_name)
        [1.0736851673414456,
         1.0615442362180327,
         1.064702686997689]

        """

        comp_type = wrapToList(comp_type)
        comp_name = wrapToList(comp_name)
        prm_name = wrapToList(prm_name)

        if not (len(comp_type) == len(comp_name) == len(prm_name)):
            raise ValueError('RAMSES: Function getPrm failed because the lists are not equal!')
        prm_values = []
        for a, b, c in zip(comp_type, comp_name, prm_name):
            prm_value = ctypes.c_double()
            retval = self._ramseslib.get_named_prm(a.encode('utf-8'), b.encode('utf-8'), c.encode('utf-8'),
                                                   prm_value)
            if retval != 0:
                raise RAMSESError(
                    'RAMSES: Function getPrm(%s,%s,%s) failed with the flag %i. Does the parameter or equipment exist? Last message was: %s'
                    % (a, b, c, retval, self.getLastErr()))
            prm_values.append(prm_value.value)
        if len(prm_values) == 1:
            return prm_values[0]
        else:
            return prm_values

    def defineSS(self, ssID, filter1, filter2, filter3):
        """Define a subsytem using three filters. The resulting list is an intersection of the filters.

        :param ssID: Number of the SS
        :type ssID: int
        :param filter1: Voltage levels to be included
        :type filter1: list of str or str
        :param filter2: Zones (which zone/zones will be included)
        :type filter2: list of str or str
        :param filter3: Bus names to be included
        :type filter3: list of str or str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0.0)
        >>> ram.defineSS(1, ['735'], [], []) # SS 1 with all buses at 735 kV, no zones, no list of buses

        .. note:: An empty filter means it is deactivated and discarded.

        """
        filter1 = wrapToList(filter1)
        filter2 = wrapToList(filter2)
        filter3 = wrapToList(filter3)

        strF1 = ' '.join(filter1)
        strF2 = ' '.join(filter2)
        strF3 = ' '.join(filter3)

        retval = self._ramseslib.define_SS(ctypes.c_int(ssID), strF1.encode('utf-8'), ctypes.c_int(len(filter1)),
                                           strF2.encode('utf-8'), ctypes.c_int(len(filter2)), strF3.encode('utf-8'),
                                           ctypes.c_int(len(filter3)))
        if retval != 0:
            raise RAMSESError('RAMSES: Function define_SS(%i,...) failed with the flag %i. Last message was: %s' % (ssID, retval, self.getLastErr()))

    def getSS(self, ssID):
        """Retrieve the buses of a subsytem.

        :param ssID: Number of the SS
        :type ssID: int

        :returns: list of buses
        :rtype: list of str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0.0)
        >>> ram.defineSS(1, ['735'], [], []) # SS 1 with all buses at 735 kV
        >>> ram.getSS(1) # get list of buses in SS 1

        """

        mxreclen = self._ramseslib.get_nbbus()
        string_buffer = ctypes.create_string_buffer(19 * mxreclen)

        retval = self._ramseslib.get_SS(ctypes.c_int(ssID), ctypes.c_int(mxreclen), string_buffer)
        if retval != 0:
            raise RAMSESError('RAMSES: Function getSS(%i) failed with the flag %i. Last message was: %s' % (ssID, retval, self.getLastErr()))

        return string_buffer.value.split()

    def getTrfoSS(self, ssID, location, in_service, rettype):
        """Retrieve transformer information of subsystem after applying some filters

        :param ssID: Number of the SS
        :type ssID: int
        :param location: 1 – both buses inside SS, 2 - tie transformers, 3 – 1 & 2
        :type location: int
        :param in_service: 1 – transformers in service, 2 - all transformers
        :type in_service: int
        :param rettype: Type of response (NAME, From, To, Status, Tap, Currentf, Currentt, Pf, Qf, Pt, Qt).
        :type rettype: str

        :returns: list of transformer names
        :rtype: list of str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0.0)
        >>> ram.defineSS(1, ['735'], [], []) # SS 1 with all buses at 735 kV
        >>> ram.getTrfoSS(1,3,2,'Status')

        .. note:: Tap is not implemented yet.

        .. todo:: Implement Taps after discussing with Lester.
        """

        if rettype not in ['NAME', 'From', 'To', 'Status', 'Tap', 'Currentf', 'Currentt', 'Pf', 'Qf', 'Pt', 'Qt']:
            raise RAMSESError('RAMSES: Function getTrfoSS(%i,%i,%i,%s): rettype is not valid!' % (
                ssID, location, in_service, rettype))
        elif location not in [1, 2, 3]:
            raise RAMSESError('RAMSES: Function getTrfoSS(%i,%i,%i,%s): location is not valid!' % (
                ssID, location, in_service, rettype))
        elif in_service not in [1, 2]:
            raise RAMSESError('RAMSES: Function getTrfoSS(%i,%i,%i,%s): in_service is not valid!' % (
                ssID, location, in_service, rettype))

        mxreclen = self._ramseslib.get_nbbra()
        string_buffer = ctypes.create_string_buffer(21 * mxreclen)
        dp_vec = (ctypes.c_double * mxreclen)()
        dp_int = (ctypes.c_int * mxreclen)()
        elem = ctypes.c_int()

        retval = self._ramseslib.get_transformer_in_SS(ctypes.c_int(ssID), ctypes.c_int(location),
                                                       ctypes.c_int(in_service), rettype.encode('utf-8'),
                                                       ctypes.c_int(mxreclen), string_buffer, dp_vec, dp_int, elem)
        if retval != 0:
            raise RAMSESError('RAMSES: Function getTrfoSS(%i,%i,%i,%s) failed with the flag %i.' % (
                ssID, location, in_service, rettype, retval))

        if elem == 0:
            return []
        elif rettype in ['Tap', 'Status']:
            return [dp_int[i] for i in range(0, elem.value)]
        elif rettype in ['Currentf', 'Currentt', 'Pf', 'Qf', 'Pt', 'Qt']:
            return [dp_vec[i] for i in range(0, elem.value)]
        else:
            return string_buffer.value.split()

    def getPrmNames(self, comp_type, comp_name):
        """Get the named parameters of a model

        :param comp_type: the types of components (EXC, TOR, INJ, DCTL, TWOP)
        :type comp_type: list of str or str
        :param comp_name: the names of component instances
        :type comp_name: list of str or str

        :returns: list of parameter names
        :rtype: list of lists of strings

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 0.0) # initialize and wait
        >>> comp_type = ['EXC','EXC','EXC']
        >>> comp_name = ['g1','g2','g3'] # name of synchronous machines
        >>> ram.getPrmNames(comp_type,comp_name)

        """
        comp_type = wrapToList(comp_type)
        comp_name = wrapToList(comp_name)

        if not (len(comp_type) == len(comp_name)):
            raise ValueError('RAMSES: Function getPrmNames failed because the lists are not equal!')
        prm_names = []
        mxprm = self._ramseslib.get_mxprm()  # get maximum number of parameters in any model
        for a, b in zip(comp_type, comp_name):
            string_buffer = ctypes.create_string_buffer(11 * mxprm)
            retval = self._ramseslib.get_comp_prm_names(a.encode('utf-8'), b.encode('utf-8'), ctypes.c_int(mxprm),
                                                        string_buffer)
            if retval != 0:
                raise RAMSESError(
                    'RAMSES: Function getPrm(%s,%s) failed with the flag %i. Does the parameter or equipment exist?'
                    % (a, b, retval))
            decodedstring = string_buffer.value.decode()
            prm_names.append(decodedstring.split())
        if len(prm_names) == 1:
            return prm_names[0]
        else:
            return prm_names

    def getObs(self, comp_type, comp_name, obs_name):
        """Get the value of a named observable. 

        :param comp_type: the types of components ('EXC','TOR','INJ','TWOP','DCTL','SYN')
        :type comp_type: list of str
        :param comp_name: the names of components
        :type comp_name: list of str
        :param obs_name: the names of observables
        :type obs_name: list of str

        :returns: list of observable values
        :rtype: list of floats

        .. note:: 
          
          For the synchronous generator ('SYN') the accepted obs_name values are 
          - 'P': Active power (MW)
          - 'Q': Reactive power (MVAr)
          -'Omega': Machine speed (pu)
          - 'S': Apparent power (MVA)
          - 'SNOM': Nominal apparent power (MVA)
          - 'PNOM': Nominal active power (MW)

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 10.0) # simulate until 10 seconds and pause
        >>> comp_type = ['INJ','EXC','TOR']
        >>> comp_name = ['L_11','g2','g3']
        >>> obs_name = ['P','vf','Pm']
        >>> ram.getObs(comp_type,comp_name, obs_name)
        [199.73704732259995,
        1.3372945282585218,
        0.816671075203357]

        """
        comp_type = wrapToList(comp_type)
        comp_name = wrapToList(comp_name)
        obs_name = wrapToList(obs_name)

        if not (len(comp_type) == len(comp_name) == len(obs_name)):
            raise ValueError('RAMSES: Function getObs failed because the lists are not equal!')
        obs_values = []
        for a, b, c in zip(comp_type, comp_name, obs_name):
            obs_value = ctypes.c_double()
            retval = self._ramseslib.get_named_obs(a.encode('utf-8'), b.encode('utf-8'), c.encode('utf-8'),
                                                   obs_value)
            if retval != 0:
                raise RAMSESError(
                    'RAMSES: Function getObs(%s,%s,%s) failed with the flag %i. Does the observable or equipment exist?'
                    % (a, b, c, retval))
            obs_values.append(obs_value.value)
        return obs_values

    def pauseSim(self, t_pause):
        """Pause the simulation at the t_pause time

        :param t_pause: pause time
        :type t_pause: float

        """
        return self._ramseslib.set_pause_time(t_pause)

    def addDisturb(self, t_dist, disturb):
        """Add a new disturbance at a specific time. Follows the same structure as the disturbances in the dst files.

        :param t_dist: time of the disturbance
        :type t_dist: float
        :param disturb: description of disturbance
        :type disturb: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case, 80.0) # simulate until 80 seconds and pause
        >>> ram.addDisturb(100.000, 'CHGPRM DCTL 1-1041  Vsetpt -0.05 0') # Decrease the setpoint of the DCTL by 0.015 pu, at t=100 s
        >>> ram.addDisturb(100.000, 'CHGPRM DCTL 2-1042  Vsetpt -0.05 0')
        >>> ram.addDisturb(100.000, 'CHGPRM DCTL 3-1043  Vsetpt -0.05 0')
        >>> ram.addDisturb(100.000, 'CHGPRM DCTL 4-1044  Vsetpt -0.05 0')
        >>> ram.addDisturb(100.000, 'CHGPRM DCTL 5-1045  Vsetpt -0.05 0')
        >>> ram.contSim(ram.getInfTime()) # continue the simulation
        """
        return self._ramseslib.add_disturb(t_dist, disturb.encode('utf-8'))

    def load_MDL(MDLName):
        """Load external DLL file with user defined models. Should be in current directory or absolute path.

        :param MDLName: path to file
        :type MDLName: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> ram = pyramses.load_MDL("MDLs.dll")
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case) # simulate
        """
        return self._ramseslib.c_load_MDL(MDLName.encode('utf-8'))

    def unload_MDL(MDLName):
        """Unload external DLL file with user defined models. Should be in current directory or absolute path.

        :param MDLName: path to file
        :type MDLName: str

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> ram = pyramses.load_MDL("MDLs.dll")
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case) # simulate
        >>> ram = pyramses.unload_MDL("MDLs.dll")
        """
        return self._ramseslib.c_unload_MDL(MDLName.encode('utf-8'))


    def get_MDL_no():
        """Unload external DLL file with user defined models. Should be in current directory or absolute path.

        :returns: list of observable values
        :rtype: list of floats

        :Example:

        >>> import pyramses
        >>> ram = pyramses.sim()
        >>> ram = pyramses.load_MDL("MDLs.dll")
        >>> case = pyramses.cfg("cmd.txt")
        >>> ram.execSim(case) # simulate
        >>> ram = pyramses.get_MDL_no()
        """
        return self._ramseslib.c_get_MDL_no()
        

    
#int get_MDL_names(int mxreclen, char *DLL_Names);