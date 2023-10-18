import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from data.example_small import create_data_model
# from data.example_data import create_data_model

##############################################################################
# Initialisation
##############################################################################
data = create_data_model()
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
delta = 1
phi_i = 1
phi_v = 1


##############################################################################
# Variables
##############################################################################
n = data['counts']['nodes'] * data['counts']['vehicles']
# M = float('inf')
M = 9999999

 # S(i, j) - binary assignment that node i is visited before node j
#S = [[None for _ in range(i+1, data['counts']['nodes'])] for i in range(data['counts']['nodes'])]
S_ij = model.S_ij = pyo.VarList(domain=pyo.Binary) # Node i visited before Node j
for i in range(data['counts']['nodes']):
    for j in range(data['counts']['nodes']):
        S_ij.add()

# X(p, v) - binary assignment of vehicle v to depot p
X_pv = model.X_pv = pyo.VarList(domain=pyo.Binary) # Vehicle v assigned to Depot p
for v in range(data['counts']['vehicles']):
    for p in range(data['counts']['depots']):
        X_pv.add()

 # Y(i,v) - binary assignment of vehicle v to node i
Y_iv = model.Y_iv = pyo.VarList(domain=pyo.Binary) # Vehicle v assigned to Node i
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        Y_iv.add()

# a(i)
early_service_vio_i = model.early_service_vio_i = pyo.VarList()
for i in range(data['counts']['nodes']):
    early_service_vio_i.add()

# b(i)
late_service_vio_i = model.late_service_vio_i = pyo.VarList()
for i in range(data['counts']['nodes']):
    late_service_vio_i.add()

#delta_T(v)
overtime_vio_v = model.overtime_vio_v = pyo.VarList()
for i in range(data['counts']['vehicles']):
    overtime_vio_v.add()

# C(i) - Accumulated cost upto node i
accum_cost_i = model.accum_cost_i = pyo.VarList()
for i in range(data['counts']['nodes']):
    accum_cost_i.add()

# CV(v)
vehicle_cost_v = model.vehicle_cost_v = pyo.VarList()
for i in range(data['counts']['vehicles']):
    vehicle_cost_v.add()

#T(i)
arrival_time_i = model.arrival_time_i = pyo.VarList()
for i in range(data['counts']['nodes']):
    arrival_time_i.add()

# TV(v)
tour_duration_v = model.tour_duration_v = pyo.VarList()
for i in range(data['counts']['vehicles']):
    tour_duration_v.add()


##############################################################################
# Objective
##############################################################################
def get_vehicle_cost(v):
    summation = sum([X_pv[get_vehicle_depot_index(v, p, data['counts']['depots'])+1] for p in range(data['counts']['depots'])])
    return data['fixed_vehicle_cost'][v] * summation

total_vehicle_cost = sum([get_vehicle_cost(v) + data['labour_cost'] * tour_duration_v[v+1] + vehicle_cost_v[v+1] + data['vehicle_T_penalty'][v] * overtime_vio_v[v+1] for v in range(data['counts']['vehicles'])])
total_node_cost = sum([data['node_T_penalty'][i] * (early_service_vio_i[i+1] + late_service_vio_i[i+1]) for i in range(data['counts']['nodes'])])
# model.obj = pyo.Objective(expr= total_vehicle_cost + total_node_cost, sense=pyo.minimize)
model.obj = pyo.Objective(expr= total_node_cost, sense=pyo.minimize)

##############################################################################
# Constraints
##############################################################################

# Constraint 4
C4 = model.C4 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for p in range(data['counts']['depots']):
        for i in range(data['counts']['nodes']):
            vp_index = get_vehicle_depot_index(v, p, data['counts']['depots'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            C4.add(expr= 
                accum_cost_i[i+1] >= data['distance_matrix'][p][i] * 
                (X_pv[vp_index+1] +
                 Y_iv[iv_index+1]
                 -1
                )
            )

# Constraint 5a
C_5a = model.C_5a = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for j in range(i+1, data['counts']['nodes']):
            nodes_index = get_node_to_node_index(i, j, data['counts']['nodes'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            jv_index = get_node_vehicle_index(j, v, data['counts']['vehicles'])
            C_5a.add(expr=
                accum_cost_i[j+1] >=
                accum_cost_i[i+1] +
                data['distance_matrix'][i][j] -
                M * (1 - S_ij[nodes_index+1]) -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 5B
C_5B = model.C_5B = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for j in range(i+1, data['counts']['nodes']):
            nodes_index = get_node_to_node_index(j, i, data['counts']['nodes'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            jv_index = get_node_vehicle_index(j, v, data['counts']['vehicles'])
            C_5B.add(expr=
                accum_cost_i[i+1] >=
                accum_cost_i[j+1] +
                data['distance_matrix'][i][j] -
                M * S_ij[nodes_index+1] -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 6
C_6 = model.C_6 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for p in range(data['counts']['depots']):
            pv_index = get_vehicle_depot_index(v, p, data['counts']['depots'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            C_6.add(expr=
                vehicle_cost_v[v+1] >=
                accum_cost_i[i+1] +
                data['distance_matrix'][i][p] -
                M * (2 - X_pv[pv_index+1] - Y_iv[iv_index+1])
            )

# Constraint 7
C_7 = model.C_7 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for p in range(data['counts']['depots']):
            pv_index = get_vehicle_depot_index(v, p, data['counts']['depots'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            C_7.add(expr=
                arrival_time_i[i+1] >=
                data['time_matrix'][p][i] *
                (X_pv[pv_index+1] + Y_iv[iv_index+1] - 1)
            )

# Constraint 8a
C_8a = model.C_8a = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for j in range(i+1, data['counts']['nodes']):
            ij_index = get_node_to_node_index(i, j, data['counts']['nodes'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            jv_index = get_node_vehicle_index(j, v, data['counts']['vehicles'])
            C_8a.add(expr=
                arrival_time_i[j+1] >=
                arrival_time_i[i+1] +
                data['service_time'][i] +
                data['time_matrix'][i][j] -
                M * (1 - S_ij[ij_index+1]) -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 8b
C_8b = model.C_8b = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for j in range(i+1, data['counts']['nodes']):
            ij_index = get_node_to_node_index(i, j, data['counts']['nodes'])
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            jv_index = get_node_vehicle_index(j, v, data['counts']['vehicles'])
            C_8b.add(expr=
                arrival_time_i[i+1] >=
                arrival_time_i[j+1] +
                data['service_time'][j] +
                data['time_matrix'][j][i] -
                M * S_ij[ij_index+1] -
                M * (2 - Y_iv[iv_index+1] - Y_iv[jv_index+1])
            )

# Constraint 9
C_9 = model.C_9 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    for i in range(data['counts']['nodes']):
        for p in range(i+1, data['counts']['depots']):
            iv_index = get_node_vehicle_index(i, v, data['counts']['vehicles'])
            pv_index = get_vehicle_depot_index(v, p, data['counts']['depots'])
            C_9.add(expr=
                tour_duration_v[v+1] >=
                arrival_time_i[i+1] +
                data['service_time'][i] +
                data['time_matrix'][i][p] -
                M * (2 - X_pv[pv_index+1] - Y_iv[iv_index+1])
            )

# Constraint 10
C_10 = model.C_10 = pyo.ConstraintList()
for i in range(data['counts']['nodes']):
    C_10.add(expr=
        early_service_vio_i[i+1] >=
        data['time_windows'][i][0] - arrival_time_i[i+1]
    )

# Constraint 11
C_11 = model.C_11 = pyo.ConstraintList()
for i in range(data['counts']['nodes']):
    C_11.add(expr=
        late_service_vio_i[i+1] >=
        arrival_time_i[i+1] - data['time_windows'][i][1]
    )

# Constraint 12
C_12 = model.C_12 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    C_12.add(expr=
        overtime_vio_v[v+1] >=
        tour_duration_v[v+1] - data['max_work_time'][v]
    )

# Constraint 13
C_13 = model.C_13 = pyo.ConstraintList()
for v in range(data['counts']['vehicles']):
    sum_left = sum([data['node_demands'][i]*Y_iv[get_node_vehicle_index(i, v, data['counts']['vehicles'])+1] for i in range(data['counts']['nodes'])])
    sum_right = sum([X_pv[get_vehicle_depot_index(v, p, data['counts']['depots'])+1] for p in range(data['counts']['depots'])])
    C_13.add(expr=
        sum_left >=
        data['vehicle_capacities'][v] * sum_right
    )


if __name__ == '__main__':
    # print(model.pprint())
    solver = pyo.SolverFactory('glpk')
    results = solver.solve(model)
    # model.pprint()
    print(results)
