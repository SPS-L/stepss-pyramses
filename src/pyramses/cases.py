#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains the class to describe a test-case scenario in pyramses."""

import os
import tempfile
import warnings

from .globals import RAMSESError, __runTimeObs__, CustomWarning, silentremove

warnings.showwarning = CustomWarning


class cfg(object):
    """Test case description class."""

    def __init__(self, cmd=None):
        self._out = []  # output file
        self._dataset = []  # data files
        self._dstset = []  # disturbance files
        self._runobs = []  # runtime observables
        self._init = []  # initialization file
        self._disc = []  # discrete trace file
        self._cont = []  # continuous trace file
        self._obs = []  # observables file
        self._trj = []  # trajectory file
        #self._cmdfile = tempfile.NamedTemporaryFile(prefix='pyramses_', suffix='.txt', dir=os.getcwd(),
        #                                            delete=False)  # text file to pass to Ramses
        #self._cmdfile.close()

        if cmd:
            try:
                typeread = 1  # 1=data, 2=init, 3=dst, 4=trj, 5=obs,6=cont, 7=disc, 8=runtime obs
                with open(cmd) as data:
                    content = data.read().splitlines()
                    for line in content:
                        # print line
                        token = line.split()
                        if typeread == 1:
                            if len(token) > 0:
                                self.addData(line)
                            else:
                                if not self._dataset:
                                    raise Exception('RAMSES: At least one datafile is necessary in the command file.')
                                    return
                                typeread += 1
                        elif typeread == 2:
                            if len(token) > 0:
                                self.addInit(line)
                                typeread += 1
                            else:
                                typeread += 1
                        elif typeread == 3:
                            if len(token) > 0:
                                self.addDst(line)
                                typeread += 1
                            else:
                                raise Exception('RAMSES: At least one dstfile is necessary in the command file.')
                                return
                        elif typeread == 4:
                            if len(token) > 0:
                                self.addTrj(line)
                                typeread += 1
                            else:
                                typeread += 2
                        elif typeread == 5:
                            if len(token) > 0:
                                self.addObs(line)
                                typeread += 1
                            else:
                                raise Exception(
                                    'RAMSES: Since a trajectory file was defined, an observable file should be given.')
                        elif typeread == 6:
                            if len(token) > 0:
                                self.addCont(line)
                                typeread += 1
                            else:
                                typeread += 1
                        elif typeread == 7:
                            if len(token) > 0:
                                self.addDisc(line)
                                typeread += 1
                            else:
                                typeread += 1
                        elif typeread == 8:
                            if len(token) > 0:
                                self.addRunObs(line)
                            else:
                                typeread += 1
            except IOError as e:
                raise IOError("RAMSES: I/O error({0}): {1}".format(e.errno, e.strerror))

    def writeCmdFile(self, userFile=None):
        """Write command file.

        :param str userFile: The filename to write to (Optional). The complete path can be given or
                             a the path relative to the working directory (os.getcwd()). If a file is not given, then a
                             temporary is created and deleted when the object is destroyed.

        """
        if not self._dataset or not self._dstset:
            raise RAMSESError('Dataset and disturbance set cannot be empty.')

        cmdFile = ""

        try:
            for i in self._dataset:
                cmdFile = cmdFile + i + '\n'
            cmdFile = cmdFile + '\n'
            if self._init:
                cmdFile = cmdFile + self._init[0] + '\n'
            else:
                cmdFile = cmdFile + '\n'
            if self._dstset:
                cmdFile = cmdFile + self._dstset[0] + '\n'
            if self._trj:
                cmdFile = cmdFile + self._trj[0] + '\n'
                cmdFile = cmdFile + self._obs[0] + '\n'
            else:
                cmdFile = cmdFile + '\n'
            if self._cont:
                cmdFile = cmdFile + self._cont[0] + '\n'
            else:
                cmdFile = cmdFile + '\n'
            if self._disc:
                cmdFile = cmdFile + self._disc[0] + '\n'
            else:
                cmdFile = cmdFile + '\n'
            for i in self._runobs:
                cmdFile = cmdFile + i + '\n'
            cmdFile = cmdFile + '\n'
            cmdFile = cmdFile + '\n'
        except IOError as e:
            raise IOError("RAMSES: I/O error({0}): {1}".format(e.errno, e.strerror))

        if userFile == None:
            return cmdFile
        else:
            if os.path.isfile(userFile):
                warnings.warn('The file %s already exists. It will be overwritten!' % (userFile))
            text_file = open(userFile, "w")
            text_file.write(cmdFile)
            text_file.close()
            return 0

    # def __del__(self):
        # silentremove(self._cmdfile.name)

    def addInit(self, afile):
        """Define the file where the simulation initialization will be saved.
        
        The initialization file is where the simulator will write the initialization procedure output.

        :param str afile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addInit("init.trace")

        .. warning:: If the file already exists, it will be ovewritten without warning!
        """
        del self._init[:]
        if os.path.isfile(afile):
            warnings.warn('The file %s already exists. It will be overwritten!' % (afile))
        self._init.append(afile)

    def getInit(self):
        """Return initialization trace file
        
        :returns: name of file
        :rtype: str
        
        """
        if self._init:
            return self._init[0]
        else:
            return ''

    def addOut(self, afile):
        """Define the file where the simulation output will be saved.

        :param str afile: the filename. The complete path must be given.

        :Example:

        >>> import pyramses
        >>> import os
        >>> case1 = pyramses.cfg()
        >>> case1.addOut(os.path.join(os.getcwd(),'output.trace'))

        .. note:: If the file already exists, the output will be appended to that file.
        """
        del self._out[:]
        self._out.append(afile)

    def getOut(self):
        """Return output trace file
        
        :returns: name of file
        :rtype: str
        
        """
        if self._out:
            return self._out[0]
        else:
            return ''

    def addCont(self, afile):
        """Add contrinuous trace file
        
        The continuous trace file saves information about the convergence of the solution algorithm
        used inside RAMSES. This is mainly used for debugging reasons and it can slow down the execution
        of the simulation.

        :param str afile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addCont("cont.trace")

        .. warning:: If the file already exists, it will be ovewritten without warning!
        """
        del self._cont[:]
        if os.path.isfile(afile):
            warnings.warn('The file %s already exists. It will be overwritten!' % (afile))
        self._cont.append(afile)

    def getCont(self):
        """Return contrinuous trace file
        
        :returns: name of file
        :rtype: str
        
        """
        if self._cont:
            return self._cont[0]
        else:
            return ''

    def addTrj(self, afile):
        """Add trajectory file

        :param str afile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addTrj("output.trj")

        .. warning:: If the file already exists, it will be ovewritten without warning!
        """
        del self._trj[:]
        if os.path.isfile(afile):
            warnings.warn('The file %s already exists. It will be overwritten!' % (afile))
        self._trj.append(afile)

    def getTrj(self):
        """Return trajectory file
        
        :returns: name of file
        :rtype: str
        
        """
        if self._trj:
            return self._trj[0]
        else:
            return ''

    def addDisc(self, afile):
        """Add discrete trace file.
        
        The discrete trace file saves information about the discrete events in the system, these may be
        from the discrete controllers, events in the disturbance file, or from discrete variables inside
        the injector, twoport, torque, or exciter models.

        :param str afile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addDisc("disc.trace")

        .. warning:: If the file already exists, it will be ovewritten without warning!
        """
        del self._disc[:]
        if os.path.isfile(afile):
            warnings.warn('The file %s already exists. It will be overwritten!' % (afile))
        self._disc.append(afile)

    def clearDisc(self):
        """Clear discrete trace file

        """
        del self._disc[:]

    def getDisc(self):
        """Return discrete trace file
        
        :returns: name of discrete trace file
        :rtype: str
        
        """
        if self._disc:
            return self._disc[0]
        else:
            return ''

    def addRunObs(self, runobs):
        """Add runtime observable.
        
        This defines some states that will be displayed during the simulation using gnuplot.
        
        :param str runobs: Description of runtime observable as defined in the RAMSES userguide
        
        :Example:        
        
        - BV BUSNAME: Voltage magnitude of bus::
   
           >>> case.addRunObs('BV 1041') # observe the bus voltage of bus 1041
        
        - MS SYNHRONOUS_MACHINE: Synchronous speed of machine::
        
           >>> case.addRunObs('MS g1')
           
        - RT RT: Real-time vs simulated time plot::
        
           >>> case.addRunObs('RT RT')
           
        - BPE/BQE/BPO/BQO BRANCH_NAME: Branch active (P), reactive (Q) power at the origin (O) or extremity (E) of a branch::
        
           >>> case.addRunObs('BPE 1041-01') # active power at the origin of branch 1041-01
        
        - ON INJECTOR_NAME OBSERVABLE_NAME: Monitor a named observable from an injector ::

           >>> case.addRunObs('ON WT1a Pw') # observable Pw from injector WT1a


        """
        if __runTimeObs__:
            if runobs not in self._runobs:
                self._runobs.append(runobs)
        else:
            warnings.warn('Gnuplot is not the path, so runtime observables are disabled.')

    def clearRunObs(self):
        """Clear runtime observables

        """
        del self._runobs[:]

    def addObs(self, ofile):
        """Add observables file

        :param str ofile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addObs("obs.dat")

        """
        if os.path.isfile(ofile):
            del self._obs[:]
            self._obs.append(ofile)
        else:
            raise IOError('RAMSES: The observables file %s does not exist or is not valid.' % (ofile))

    def getObs(self):
        """Get observables file name
        
        :returns: name of observables file
        :rtype: str
        
        """
        if self._obs:
            return self._obs[0]
        else:
            return ''

    def addData(self, datafile):
        """Add datafile in the dataset.
        
        The data files provide a description of the system to be simulated, along with the solver parameters.

        :param str datafile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addData("dyn_A.dat")

        .. warning:: At least one file needs to be added.
        """
        if os.path.isfile(datafile):
            if datafile not in self._dataset:
                self._dataset.append(datafile)
        else:
            raise IOError('RAMSES: The datafile %s does not exist or is not valid.' % (datafile))

    def getData(self):
        """Get datafile list
        
        :returns: list of data file names
        :rtype: list
        
        """
        return self._dataset

    def delData(self, datafile):
        """Remove a specific datafile from dataset
        
        """
        if datafile in self._dataset:
            self._dataset.remove(datafile)

    def clearData(self):
        """Empty the dataset
        
        """
        del self._dataset[:]

    def addDst(self, dstfile):
        """Add dstfile in the dstset
        
        The disturbance file is where the disturbance to be simulated is described

        :param str dstfile: the filename. The complete path can be given or a the path relative to the working directory (os.getcwd())

        :Example:

        >>> import pyramses
        >>> case1 = pyramses.cfg()
        >>> case1.addDst("short.dst")

        .. warning:: A file needs to be provided for the simulation to start.
        """
        if os.path.isfile(dstfile):
            del self._dstset[:]
            self._dstset.append(dstfile)
        else:
            raise IOError('RAMSES: The dstfile %s does not exist or is not valid.' % (dstfile))

    def getDst(self):
        """Get disturbance
        
        :returns: name of disturbance file
        :rtype: str
        
        """
        if self._dstset:
            return self._dstset[0]
        else:
            return ''

    def clearDst(self):
        """Empty the dstset
        
        """
        del self._dstset[:]
