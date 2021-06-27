About
=====

PyRAMSES is a Python module that facilitates the use of the dynamic simulator RAMSES. The module provides basic functionality like defining test-cases, running a simulation, extracting information, etc. As well as more advanced integration of the simulator into the remaining Python code.

Please check the documentation under `https://pyramses.paristidou.info <https://pyramses.paristidou.info>`_.

Models included in current version:
-----------------------------------

- Injectors =  ['BESSWithChanges', 'vfd_load', 'IBG', 'indmach1', 'svc_hq_generic1', 'PQ', 'WT3WithChanges', 'WT4WithChanges', 'restld', 'theveq', 'indmach2', 'load']
- Exciters =  ['IEEET5', 'AC1A_RETRO', 'AC8B_PSS3B_lim', 'EXHQSC_PSS4B_MAXEX2', 'ST1A_PSS3B', 'ST1A_IEEEST', 'generic2', 'ST1A', 'AC4A', 'ST1A_PSS4B_OELHQ', 'generic1', 'ST1A_PSS4B', 'EXPIC1_PSS2B_MAXEX2', 'ST2A', 'DC3A', 'ST1A_PSS2B_OELHQ', 'EXHQSC_PSS4B_OELHQ', 'EXHQSC_PSS4B', 'ST1A_PSS3B_OELHQ', 'GENERIC3', 'ENTSOE_simp', 'ST1A_PSS2B', 'EXPIC1_PSS2B', 'ST1A_lim', 'AC1A_RETRO_PSS4B', 'AC8B', 'ST1A_OELHQ', 'kundur', '1storder', 'EXPIC1', 'EXHQSC_MAXEX2', 'ST1A_PSS4B_MAXEX2', 'hq_generic1', 'ST1A_PSS2B_MAXEX2', 'AC1A', 'EXHQSC', 'constant', 'GENERIC4', 'AC1A_OELHQ', 'ST1A_IEEEST_MAXEX2', 'AC1A_MAXEX2']
- Speed governors =  ['HQRVC', 'thermal_generic1', 'HQRVM', '1storder', 'DEGOV1', 'hq_generic', 'HQRVW', 'constant', 'ENTSOE_simp', 'ENTSOE_simp_consensus_mod', 'hydro_generic1', 'ENTSOE_simp_consensus', 'HQRVN', 'hq_generic1']
- Two-ports =  ['HQSVC', 'DC_BHPM', 'HVDC_LCC', 'DC_CHAAUT', 'CHENIER', 'HVDC_VSC_SC', 'vsc_hq', 'CSVGN5', 'DCL_WCL', 'HVDC_VSC']
- Discrete controllers =  ['sim_minmaxspeed', 'mais', 'ltcinv', 'FRT', 'oltc2', 'ltc', 'uvls', 'uvprot', 'pst', 'rt', 'sim_minmaxvolt', 'ltc2', 'HQmais', 'voltage_variability']

ACADEMIC PUBLIC LICENSE
=======================

Copyright (c) Dr Thierry Van Cutsem (RAMSES) and Dr Petros Aristidou (PyRAMSES). All rights reserved.

The following license governs the use of RAMSES and PyRAMSES in academic and educational environments. For uses outside this scope, or if you are unsure, contact the copyright owners.

Definitions
-----------

"Software" means a copy of RAMSES or PyRAMSES, which is distributed under this Academic Public License.
"Work based on the Software" means either the Software or any derivative work under copyright law: that is to say, a work containing the Software or a portion of it, either verbatim or with modifications.
"Using the Software" means any act of creating executables that contain or directly use libraries that are part of the Software, running any of the tools that are part of the Software, or creating works based on the Software.
"You" refers to each licensee.

License terms
-------------

- Permission is hereby granted to use the Software free of charge for any non-commercial purpose, including teaching and research at universities, colleges and other educational institutions, research at non-profit research institutions, and personal non-profit purposes. For using the Software for commercial purposes, including but not restricted to consulting activities, design of commercial hardware or software products, and a commercial entity participating in research projects, you have to contact the Authors for an appropriate license.

- You are not required to accept this License. Nothing else grants you permission to use the Software; law prohibits this action if you do not accept this License. Therefore, by using the Software (or any work based on the Software), you indicate your acceptance of this License and all its terms and conditions.

No warranty
-----------

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.