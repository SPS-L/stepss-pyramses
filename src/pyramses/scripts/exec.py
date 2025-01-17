import sys
import pyramses

def run():
    """run an execution"""
    args = sys.argv[1:]
    if len(args) != 2 or args[0] != '-t' :
        sys.exit("Wrong arguments. Usage: dynsim -t cmd.txt")
    ram = pyramses.sim()
    case = pyramses.cfg(args[1])
    case.addOut('output_temp.trace')
    ram.execSim(case)
    print("The output_temp.trace file contains the execution trace.")
    