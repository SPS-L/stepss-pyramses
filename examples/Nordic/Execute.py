# PyRAMSES Dynamic Simulation Tutorial - Nordic Test System
# 
# This script demonstrates voltage collapse analysis using PyRAMSES
# (Python-based RApid Multithreaded Simulation of Electric power Systems)
# 
# Learning Objectives:
# - Set up and configure PyRAMSES simulations
# - Analyze power system dynamic behavior following disturbances
# - Understand voltage stability mechanisms
# - Interpret simulation results and plots
#
# Documentation: https://pyramses.sps-lab.org/
# Course: https://sps-lab.org/courses/een452/

# Import required libraries
import pyramses  # Main PyRAMSES simulation engine
import os        # For file operations

# ============================================================================
# STEP 1: CONFIGURE THE SIMULATION CASE
# ============================================================================
# This section sets up all the input files and output options for the simulation
# Reference: https://pyramses.sps-lab.org/interface/case.html

print("Step 1: Configuring simulation case...")

# Create a new simulation configuration object
case = pyramses.cfg()

# Add output files for simulation results and debugging
case.addOut('output.trace')      # Main simulation log file - contains detailed execution info
case.addData('dyn_B.dat')        # Dynamic data file - contains generator models, controllers, network topology
case.addData('volt_rat_B.dat')   # Power flow solution - initial voltage magnitudes and angles at all buses
case.addData('settings1.dat')    # Solver settings - numerical integration parameters, tolerances
case.addInit('init.trace')       # Initialization log - shows how the system reaches steady state
case.addDst('nothing.dst')       # Disturbance file - defines events to occur during simulation (empty = no events)
case.addCont('cont.trace')       # Continuous variables trace - time evolution of state variables
case.addDisc('disc.trace')       # Discrete events trace - records of switching events, breaker operations
case.addObs('obs.dat')           # Observation file - defines which variables to monitor and save
case.addTrj('output.trj')        # Trajectory file - main output containing all simulation results

# ============================================================================
# STEP 2: CLEAN UP PREVIOUS SIMULATION FILES
# ============================================================================
# Remove any existing output files from previous runs to avoid confusion
# This ensures we start with a clean slate

print("Step 2: Cleaning up previous simulation files...")

# Loop through all files in current directory
for item in os.listdir('.'):
    # Remove files with .trace or .trj extensions (simulation output files)
    if item.endswith(('.trace', '.trj')):
        os.remove(os.path.join('.', item))
        print(f"  Removed: {item}")

# ============================================================================
# STEP 3: INITIALIZE THE SIMULATION
# ============================================================================
# Start the PyRAMSES simulator and initialize the system to steady state
# Reference: https://pyramses.sps-lab.org/interface/simul.html

print("Step 3: Initializing simulation...")

# Create simulation object
ram = pyramses.sim()

# Initialize the system at t=0.0 seconds
# This step:
# - Loads all data files
# - Performs power flow calculation
# - Initializes all dynamic models (generators, controllers, loads)
# - Verifies system stability at initial conditions
try:
    ram.execSim(case, 0.0)  # Initialize at time t=0.0
    print("  Initialization successful!")
except:
    print("  Initialization failed!")
    print(ram.getLastErr())  # Print any initialization errors

# ============================================================================
# STEP 4: APPLY DISTURBANCE
# ============================================================================
# Simulate a generator trip event to demonstrate voltage collapse
# This is the key event that will trigger the dynamic response

print("Step 4: Applying disturbance...")

# Trip generator 'g7' at t=10.00 seconds
# Command format: 'BREAKER SYNC_MACH [generator_name] [status]'
# - BREAKER: Type of switching action
# - SYNC_MACH: Component type (synchronous machine)
# - g7: Generator name from the data file
# - 0: Status (0 = open/off, 1 = closed/on)
ram.addDisturb(10.00, 'BREAKER SYNC_MACH g7 0')
print("  Generator g7 will be tripped at t=10.00 seconds")

# ============================================================================
# STEP 5: RUN THE DYNAMIC SIMULATION
# ============================================================================
# Simulate the system response from t=0 to t=150 seconds
# This captures the complete dynamic behavior following the disturbance

print("Step 5: Running dynamic simulation...")

try:
    # Continue simulation until t=150.0 seconds
    # During this time, the system will:
    # - Respond to the generator trip at t=10s
    # - Show frequency and voltage dynamics
    # - Demonstrate control system responses (governors, AVRs)
    # - Potentially show voltage collapse if the system is unstable
    ram.contSim(150.0)
    
    # End simulation and finalize output files
    ram.endSim()
    print("  Simulation completed successfully!")
except:
    print("  Simulation failed!")
    print(ram.getLastErr())  # Print any simulation errors

# ============================================================================
# STEP 6: OPTIONAL - VIEW SIMULATION LOG
# ============================================================================
# Uncomment the line below to see detailed simulation log
# This can be useful for debugging or understanding what happened during simulation

print("Step 6: Simulation log (optional)...")
# Uncomment the next line to see the log:
# print(open(case.getOut()).read())

# ============================================================================
# STEP 7: ANALYZE RESULTS
# ============================================================================
# Extract and plot key simulation results
# Reference: https://pyramses.sps-lab.org/interface/extractor.html

print("Step 7: Analyzing results...")

# Create extractor object to access simulation results
# This loads the trajectory file containing all time-series data
ext = pyramses.extractor(case.getTrj())

# ============================================================================
# STEP 8: PLOT DYNAMIC RESPONSES
# ============================================================================
# Generate plots showing the system response to the disturbance
# We focus on generator g5 as a representative example

print("Step 8: Generating plots...")

# Plot 1: Frequency deviation (speed) of generator g5
# This shows how the system frequency responds to the loss of generation
# Expected: Initial drop followed by recovery due to governor action
print("  Plotting frequency deviation...")
ext.getSync('g5').S.plot()

# Plot 2: Governor valve position for generator g5
# Shows the primary frequency control response
# Expected: Valve opens to increase mechanical power output
print("  Plotting governor valve position...")
ext.getTor('g5').z.plot()

# Plot 3: Mechanical power output of generator g5 (per unit)
# Shows the turbine response to frequency deviation
# Expected: Power increases to help restore system frequency
print("  Plotting mechanical power...")
ext.getTor('g5').Pm.plot()

# Plot 4: Electrical active power output of generator g5
# Shows the actual electrical power delivered to the grid
# Expected: Follows mechanical power with some dynamics
print("  Plotting electrical active power...")
ext.getSync('g5').P.plot()

# Plot 5: Terminal voltage magnitude at generator g5
# Shows voltage stability response
# Expected: May show voltage drop and recovery, or collapse if system is unstable
print("  Plotting terminal voltage...")
ext.getBus('g5').mag.plot()

# Plot 6: Electrical reactive power output of generator g5
# Shows reactive power dynamics and AVR response
# Expected: Reactive power may increase to support voltage
print("  Plotting electrical reactive power...")
ext.getSync('g5').Q.plot()

print("\n" + "="*80)
print("SIMULATION COMPLETED SUCCESSFULLY!")
print("="*80)

# ============================================================================
# INTERPRETATION GUIDE
# ============================================================================
# 
# What to look for in the plots:
# 
# 1. Frequency Response (Plot 1):
#    - Initial frequency drop indicates system stress
#    - Recovery shows governor effectiveness
#    - Steady-state deviation shows load-generation balance
#
# 2. Governor Response (Plots 2-3):
#    - Valve opening shows primary frequency control
#    - Mechanical power increase compensates for lost generation
#
# 3. Voltage Response (Plot 5):
#    - Voltage drop indicates reactive power deficiency
#    - Recovery shows AVR effectiveness
#    - Continued decline may indicate voltage collapse
#
# 4. Power Flow (Plots 4, 6):
#    - Active power redistribution shows network response
#    - Reactive power changes show voltage support efforts
#
# Expected Behavior for Voltage Collapse:
# - Initial voltage drop following generator trip
# - Gradual voltage decline in some areas
# - Possible voltage collapse if reactive reserves are insufficient
# - Frequency recovery but voltage instability
#
# This simulation demonstrates the importance of:
# - Adequate reactive power reserves
# - Proper voltage control coordination
# - System planning for N-1 contingencies
#
# For more information:
# - PyRAMSES Documentation: https://pyramses.sps-lab.org/
# - Course Website: https://sps-lab.org/courses/een452/ 