# PyRAMSES Dynamic Simulation Tutorial - Nordic Test System

This repository contains startup material for learning power system dynamics using [PyRAMSES](https://pyramses.sps-lab.org/) (Python-based RApid Multithreaded Simulation of Electric power Systems) on JupyterHub. The material is designed for the **Control and Operation of Electric Power Systems (EEN452)** course at Cyprus University of Technology.

## Overview

PyRAMSES is a time-domain, dynamic simulator for future electric power systems that enables parallel processing of large-scale power system simulations. This tutorial demonstrates voltage collapse analysis on the Nordic test system, a well-known benchmark for power system stability studies.

## Course Context

This material is part of the [EEN452 course](https://sps-lab.org/courses/een452/) taught by Prof. Petros Aristidou at the Sustainable Power Systems Lab. The course covers:

- Dynamic behavior and control structures of electric power systems
- Frequency and voltage control mechanisms
- Power system stability analysis (angle/voltage/frequency)
- Economic operation of power systems

## System Description

The Nordic test system represents a realistic power system with:
- **20 synchronous generators** (g1-g20) with detailed dynamic models
- **Multi-voltage levels**: 15kV, 20kV, 130kV, 220kV, 400kV
- **Comprehensive network**: 74 buses, 20 transformers, 52 transmission lines
- **Dynamic components**: 
  - Synchronous machines with detailed models (d-axis and q-axis dynamics)
  - Automatic voltage regulators (AVR) with generic excitation systems
  - Turbine-governor systems (hydro-generic type)
  - Power system stabilizers (PSS)

## Files Description

- **`Execute.ipynb`**: Main Jupyter notebook with step-by-step simulation instructions
- **`dyn_B.dat`**: Dynamic data file containing generator models, controllers, and network topology
- **`volt_rat_B.dat`**: Power flow solution (voltage magnitudes and angles)
- **`settings1.dat`**: Solver settings and simulation parameters
- **`obs.dat`**: Observation file defining which variables to monitor
- **`nothing.dst`**: Disturbance file (empty for initial simulation)

## Simulation Scenario

The tutorial demonstrates a **voltage collapse scenario** by:
1. Initializing the system at a stable operating point
2. Tripping generator g7 at t=10.0 seconds
3. Observing the system response over 150 seconds
4. Analyzing frequency, voltage, and power dynamics

## Key Learning Objectives

Through this simulation, students will learn to:
- Set up and configure PyRAMSES simulations
- Analyze power system dynamic behavior
- Understand voltage stability mechanisms
- Interpret simulation results and plots
- Use PyRAMSES extractor tools for post-processing

## Getting Started

### Prerequisites
- JupyterLab with PyRAMSES installed
- Basic knowledge of power system dynamics
- Familiarity with Python programming

### Installation
```bash
pip install matplotlib scipy numpy mkl jupyter ipython pyramses
```

### Running the Simulation
1. Load the folder in JupyterHub
2. Open `Execute.ipynb`
3. Run cells sequentially to:
   - Configure the simulation case
   - Initialize the system
   - Apply the disturbance (generator trip)
   - Simulate the dynamic response
   - Plot and analyze results

## Expected Results

The simulation will show:
- **Frequency deviation** following the generator trip
- **Voltage dynamics** at various buses
- **Power flow redistribution** in the network
- **Governor and AVR responses** to maintain system stability

## Documentation and References

- [PyRAMSES Documentation](https://pyramses.sps-lab.org/)
- [Course Website](https://sps-lab.org/courses/een452/)
- [Original Voltage Collapse Paper](https://orbi.uliege.be/handle/2268/245565)

## Technical Details

The Nordic system operates at 50Hz and includes:
- **Total generation capacity (incl. external equivalent)**: 15,000 MW
- **Network topology**: Meshed transmission system
- **Control systems**: Primary frequency control, voltage control
- **Stability margins**: Designed to demonstrate voltage collapse phenomena

## Support

For technical issues with PyRAMSES, refer to the [official documentation](https://pyramses.sps-lab.org/). For course-related questions, contact the instructor through the [course website](https://sps-lab.org/courses/een452/).

---

*This material is part of the EEN452 course curriculum at Cyprus University of Technology, developed by the Sustainable Power Systems Lab.*
