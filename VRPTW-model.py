import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import vrplib

##############################################################################
# Initialisation
##############################################################################
model = pyo.ConcreteModel()

##############################################################################
# Get indexes
##############################################################################

def get_node_to_node_index(node_i, node_j, num_nodes):
    return node_i * num_nodes + node_j

def get_vehicle_depot_index(vehicle_v, depot_p, num_depots):
    return vehicle_v * num_depots + depot_p

def get_node_vehicle_index(node_i, vehicle_v, num_vehicles):
    return node_i * num_vehicles + vehicle_v

##############################################################################
# Parameters
##############################################################################
vrp_instance = vrplib.read_instance('./data/C101(25).txt', instance_format='solomon')
time_matrix = vrp_instance['edge_weight']
num_depots = 1
fixed_vehicle_cost = 0
tw_penalty_cost = [999999] * len(vrp_instance['demand'])
max_vehicle_work_time = [8.0] * vrp_instance['vehicles']
vehicle_time_penalty_cost = [999999] * vrp_instance['vehicles']
labour_cost = 1

delta = 1
phi_i = 1
phi_v = 1


##############################################################################
# Variables
##############################################################################
n = len(vrp_instance['demand']) * vrp_instance['vehicles']
# M = float('inf')
M = 9999999

 # S(i, j) - binary assignment that node i is visited before node j
#S = [[None for _ in range(i+1, len(vrp_instance['demand'])] for i in range(len(vrp_instance['demand'])]
S_ij = model.S_ij = pyo.VarList(domain=pyo.Binary) # Node i visited before Node j
for i in range(len(vrp_instance['demand'])):
    for j in range(len(vrp_instance['demand'])):
        S_ij.add()

# X(p, v) - binary assignment of vehicle v to depot p
X_pv = model.X_pv = pyo.VarList(domain=pyo.Binary) # Vehicle v assigned to Depot p
for v in range(vrp_instance['vehicles']):
    for p in range(num_depots):
        X_pv.add()

 # Y(i,v) - binary assignment of vehicle v to node i
Y_iv = model.Y_iv = pyo.VarList(domain=pyo.Binary) # Vehicle v assigned to Node i
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        Y_iv.add()

# a(i)
early_service_vio_i = model.early_service_vio_i = pyo.VarList()
for i in range(len(vrp_instance['demand'])):
    early_service_vio_i.add()

# b(i)
late_service_vio_i = model.late_service_vio_i = pyo.VarList()
for i in range(len(vrp_instance['demand'])):
    late_service_vio_i.add()

#delta_T(v)
overtime_vio_v = model.overtime_vio_v = pyo.VarList()
for i in range(vrp_instance['vehicles']):
    overtime_vio_v.add()

# C(i) - Accumulated cost upto node i
accum_cost_i = model.accum_cost_i = pyo.VarList()
for i in range(len(vrp_instance['demand'])):
    accum_cost_i.add()

# CV(v)
vehicle_cost_v = model.vehicle_cost_v = pyo.VarList()
for i in range(vrp_instance['vehicles']):
    vehicle_cost_v.add()

#T(i)
arrival_time_i = model.arrival_time_i = pyo.VarList()
for i in range(len(vrp_instance['demand'])):
    arrival_time_i.add()

# TV(v)
tour_duration_v = model.tour_duration_v = pyo.VarList()
for i in range(vrp_instance['vehicles']):
    tour_duration_v.add()


##############################################################################
# Objective
##############################################################################
def get_vehicle_cost(v):
    summation = sum([X_pv[get_vehicle_depot_index(v, p, num_depots)+1] for p in range(num_depots)])
    return fixed_vehicle_cost * summation

total_vehicle_cost = sum([
    get_vehicle_cost(v) \
        + labour_cost * tour_duration_v[v+1] \
        + vehicle_cost_v[v+1] \
        + vehicle_time_penalty_cost[v] * overtime_vio_v[v+1]
    for v in range(vrp_instance['vehicles'])
])
total_node_cost = sum([tw_penalty_cost[i] * (early_service_vio_i[i+1] + late_service_vio_i[i+1]) for i in range(len(vrp_instance['demand']))])
model.obj = pyo.Objective(expr= total_vehicle_cost + total_node_cost, sense=pyo.minimize)
# model.obj = pyo.Objective(expr= total_node_cost, sense=pyo.minimize)

##############################################################################
# Constraints
##############################################################################
# Constraint 1 is objective function

# Constraint 2
C2 = model.C2 = pyo.ConstraintList()
for i in range(len(vrp_instance['demand'])):
    vehicle_assignment = 0
    for v in range(vrp_instance['vehicles']):
        iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
        vehicle_assignment += Y_iv[iv_index+1]
    C2.add(expr=
        vehicle_assignment == 1
    )

# Constraint 3
C3 = model.C3 = pyo.ConstraintList()
for p in range(num_depots):
    depot_assignment = 0
    for v in range(vrp_instance['vehicles']):
        vp_index = get_vehicle_depot_index(v, p, num_depots)
        depot_assignment += X_pv[vp_index+1]
    C3.add(expr=
        depot_assignment == 1
    )

# Constraint 4
C4 = model.C4 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for p in range(num_depots):
        for i in range(len(vrp_instance['demand'])):
            vp_index = get_vehicle_depot_index(v, p, num_depots)
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            C4.add(expr=
                accum_cost_i[i+1] >= vrp_instance['edge_weight'][p][i] *
                (X_pv[vp_index+1] +
                 Y_iv[iv_index+1]
                 -1
                )
            )

# Constraint 5a
C_5a = model.C_5a = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for j in range(i+1, len(vrp_instance['demand'])):
            nodes_index = get_node_to_node_index(i, j, len(vrp_instance['demand']))
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            jv_index = get_node_vehicle_index(j, v, vrp_instance['vehicles'])
            C_5a.add(expr=
                accum_cost_i[j+1] >=
                accum_cost_i[i+1] +
                vrp_instance['edge_weight'][i][j] -
                M * (1 - S_ij[nodes_index+1]) -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 5B
C_5B = model.C_5B = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for j in range(i+1, len(vrp_instance['demand'])):
            nodes_index = get_node_to_node_index(j, i, len(vrp_instance['demand']))
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            jv_index = get_node_vehicle_index(j, v, vrp_instance['vehicles'])
            C_5B.add(expr=
                accum_cost_i[i+1] >=
                accum_cost_i[j+1] +
                vrp_instance['edge_weight'][i][j] -
                M * S_ij[nodes_index+1] -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 6
C_6 = model.C_6 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for p in range(num_depots):
            pv_index = get_vehicle_depot_index(v, p, num_depots)
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            C_6.add(expr=
                vehicle_cost_v[v+1] >=
                accum_cost_i[i+1] +
                vrp_instance['edge_weight'][i][p] -
                M * (2 - X_pv[pv_index+1] - Y_iv[iv_index+1])
            )

# Constraint 7
C_7 = model.C_7 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for p in range(num_depots):
            pv_index = get_vehicle_depot_index(v, p, num_depots)
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            C_7.add(expr=
                arrival_time_i[i+1] >=
                time_matrix[p][i] *
                (X_pv[pv_index+1] + Y_iv[iv_index+1] - 1)
            )

# Constraint 8a
C_8a = model.C_8a = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for j in range(i+1, len(vrp_instance['demand'])):
            ij_index = get_node_to_node_index(i, j, len(vrp_instance['demand']))
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            jv_index = get_node_vehicle_index(j, v, vrp_instance['vehicles'])
            C_8a.add(expr=
                arrival_time_i[j+1] >=
                arrival_time_i[i+1] +
                vrp_instance['service_time'][i] +
                time_matrix[i][j] -
                M * (1 - S_ij[ij_index+1]) -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 8b
C_8b = model.C_8b = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for j in range(i+1, len(vrp_instance['demand'])):
            ij_index = get_node_to_node_index(i, j, len(vrp_instance['demand']))
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            jv_index = get_node_vehicle_index(j, v, vrp_instance['vehicles'])
            C_8b.add(expr=
                arrival_time_i[i+1] >=
                arrival_time_i[j+1] +
                vrp_instance['service_time'][j] +
                time_matrix[j][i] -
                M * S_ij[ij_index+1] -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 9
C_9 = model.C_9 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    for i in range(len(vrp_instance['demand'])):
        for p in range(i+1, num_depots):
            iv_index = get_node_vehicle_index(i, v, vrp_instance['vehicles'])
            pv_index = get_vehicle_depot_index(v, p, num_depots)
            C_9.add(expr=
                tour_duration_v[v+1] >=
                arrival_time_i[i+1] +
                vrp_instance['service_time'][i] +
                time_matrix[i][p] -
                M * (2 - X_pv[pv_index+1] - Y_iv[iv_index+1])
            )

# Constraint 10
C_10 = model.C_10 = pyo.ConstraintList()
for i in range(len(vrp_instance['demand'])):
    C_10.add(expr=
        early_service_vio_i[i+1] >=
        vrp_instance['time_window'][i][0] - arrival_time_i[i+1]
    )

# Constraint 11
C_11 = model.C_11 = pyo.ConstraintList()
for i in range(len(vrp_instance['demand'])):
    C_11.add(expr=
        late_service_vio_i[i+1] >=
        arrival_time_i[i+1] - vrp_instance['time_window'][i][1]
    )

# Constraint 12
C_12 = model.C_12 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    C_12.add(expr=
        overtime_vio_v[v+1] >=
        tour_duration_v[v+1] - max_vehicle_work_time[v]
    )

# Constraint 13
C_13 = model.C_13 = pyo.ConstraintList()
for v in range(vrp_instance['vehicles']):
    sum_left = sum([
        vrp_instance['demand'][i] * Y_iv[get_node_vehicle_index(i, v, vrp_instance['vehicles'])+1]
        for i in range(len(vrp_instance['demand']))
    ])
    sum_right = sum([
        X_pv[get_vehicle_depot_index(v, p, num_depots)+1]
        for p in range(num_depots)
    ])
    C_13.add(expr=
        sum_left >=
        vrp_instance['capacity'] * sum_right
    )


if __name__ == '__main__':
    # print(model.pprint())
    solver = pyo.SolverFactory('glpk')
    results = solver.solve(model)
    # model.pprint()
    print(results)
