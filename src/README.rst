About
-----

PyRAMSES is a Python module that facilitates the use of the dynamic simulator RAMSES. The module provides basic functionality like defining test-cases, running a simulation, extracting information, etc. As well as more advanced integration of the simulator into the remaining Python code.

Please check the documentation under `https://pyramses.sps-lab.org <https://pyramses.sps-lab.org>`_.

Models included in current version:
-----------------------------------

- Injectors =  ['BESSWithChanges', 'vfd_load', 'IBG', 'indmach1', 'svc_hq_generic1', 'PQ', 'WT3WithChanges', 'WT4WithChanges', 'restld', 'theveq', 'indmach2', 'load']
- Exciters =  ['IEEET5', 'AC1A_RETRO', 'AC8B_PSS3B_lim', 'EXHQSC_PSS4B_MAXEX2', 'ST1A_PSS3B', 'ST1A_IEEEST', 'generic2', 'ST1A', 'AC4A', 'ST1A_PSS4B_OELHQ', 'generic1', 'ST1A_PSS4B', 'EXPIC1_PSS2B_MAXEX2', 'ST2A', 'DC3A', 'ST1A_PSS2B_OELHQ', 'EXHQSC_PSS4B_OELHQ', 'EXHQSC_PSS4B', 'ST1A_PSS3B_OELHQ', 'GENERIC3', 'ENTSOE_simp', 'ST1A_PSS2B', 'EXPIC1_PSS2B', 'ST1A_lim', 'AC1A_RETRO_PSS4B', 'AC8B', 'ST1A_OELHQ', 'kundur', '1storder', 'EXPIC1', 'EXHQSC_MAXEX2', 'ST1A_PSS4B_MAXEX2', 'hq_generic1', 'ST1A_PSS2B_MAXEX2', 'AC1A', 'EXHQSC', 'constant', 'GENERIC4', 'AC1A_OELHQ', 'ST1A_IEEEST_MAXEX2', 'AC1A_MAXEX2']
- Speed governors =  ['HQRVC', 'thermal_generic1', 'HQRVM', '1storder', 'DEGOV1', 'hq_generic', 'HQRVW', 'constant', 'ENTSOE_simp', 'ENTSOE_simp_consensus_mod', 'hydro_generic1', 'ENTSOE_simp_consensus', 'HQRVN', 'hq_generic1']
- Two-ports =  ['HQSVC', 'DC_BHPM', 'HVDC_LCC', 'DC_CHAAUT', 'CHENIER', 'HVDC_VSC_SC', 'vsc_hq', 'CSVGN5', 'DCL_WCL', 'HVDC_VSC']
- Discrete controllers =  ['sim_minmaxspeed', 'mais', 'ltcinv', 'FRT', 'oltc2', 'ltc', 'uvls', 'uvprot', 'pst', 'rt', 'sim_minmaxvolt', 'ltc2', 'HQmais', 'voltage_variability']