import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import vrplib

vrp_instance = vrplib.read_instance('./data/C101(25).txt', instance_format='solomon')

print(vrp_instance['time_window'][1][1])