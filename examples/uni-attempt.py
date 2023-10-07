"""
Created on Wed May 12 19:15:33 2021

@author: Arno Theron

"""


import cplex
from cplex.exceptions import CplexError

convex = True

def data_model():
    """Stores the data for the problem."""
    data = {}
    # Distance from node i to node j
    data['distance_matrix'] = [
        [
            0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
            468, 776, 662
        ],
        [
            548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            320, 1084, 514
        ],
        [
            194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            274, 810, 468
        ],
        [
            536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    ]
    data['num_vehicles'] = 4
    data['depot'] = 0
    data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data['vehicle_capacities'] = [15, 15, 15, 15]
    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ]
    data['time_windows'] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    data['node_T_penalty'] = [1.0] * len(data['demands'])
    data['vehicle_T_penalty'] = [1.0] * data['num_vehicles']
    data['max_work_time'] = [8.0] * data['num_vehicles']
    
    return data
    

def model():
    """Data initialisation"""
    data = data_model()
    nbDepot = 2
    nbDemand = len(data['demands'])
    nbSupply = data['num_vehicles']
    n = nbDemand * nbSupply   
    rho_i = data['node_T_penalty']
    rho_v = data['vehicle_T_penalty']
    labour_c = 1.0
    vehicle_cost = 1.0
    M = 1000000.0
    
    # Index of vehicle v and node i
    def varindex(v, i):
        return v * nbDemand + i
    
    # Index of depot p, vehicle v and node i
    def lngvarindex(p, v, i):
        return p * nbSupply * nbDemand + v * nbDemand + i
    
    # Model
    model = cplex.Cplex()
    model.set_problem_name("Transport Problem")
    model.objective.set_sense(model.objective.sense.minimize)
    
    """Variables"""
    # S(i, j) - binary assignment that node i is visited before node j
    colname_S = []
    for i in range(nbDemand):
        for j in range(i+1, nbDemand):
            colname_S.append(f"S({i},{j})")
    length_S = len(colname_S)
    #colname_S = [f"S{ij}" for ij in range(nbDemand**2)]
    model.variables.add(obj=[0.0] * length_S, 
                        lb=[0.0] * length_S,
                        ub=[1.0] * length_S, 
                        types=[model.variables.type.binary] * length_S, 
                        names=colname_S)
    
    
    # X(p, v) - binary assignment of vehicle v to depot p
    colname_x = [f"X{pv}" for pv in range(nbSupply*nbDepot)]
    model.variables.add(obj=[vehicle_cost] * nbSupply*nbDepot, ## Question
                        lb=[0.0] * nbSupply*nbDepot,
                        ub=[1.0] * nbSupply*nbDepot, 
                        types=[model.variables.type.binary] * nbSupply*nbDepot, 
                        names=colname_x)
    
    # Y(i,v) - binary assignment of vehicle v to node i
    colname_Y = [f'Y{iv+1}' for iv in range(n-4)]
    model.variables.add(obj=[0.0] * (n-4),
                        lb = [0.0] * (n-4),
                        ub = [1.0] * (n-4),
                        types=[model.variables.type.binary] * (n-4),
                        names=colname_Y)
    
    # delta_a(i) - Early TW violation for node i
    colname_da = [f'da{i}' for i in range(nbDemand)]
    model.variables.add(obj=rho_i, 
                        lb=[0.0] * nbDemand, 
                        ub=[cplex.infinity] * nbDemand, 
                        names=colname_da)
    
    # delta_b(i) - Late TW violation for node i
    colname_db = [f'db{i}' for i in range(nbDemand)]
    model.variables.add(obj=rho_i, 
                        lb=[0.0] * nbDemand, 
                        ub=[cplex.infinity] * nbDemand, 
                        names=colname_db)
    
    # delta_T(v) - working time violation for vehicle v
    colname_dT = [f'dT{v}' for v in range(nbSupply)]
    model.variables.add(obj=rho_v, 
                        lb=[0.0] * nbSupply, 
                        ub=[cplex.infinity] * nbSupply, 
                        names=colname_dT)
    
    # C(i) - Accumulated distance cost for vehicle to node i
    colname_C = [f'C{i}' for i in range(nbDemand)]
    model.variables.add(obj=[0.0] * nbDemand, 
                        lb=[0.0] * nbDemand, 
                        ub=[cplex.infinity] * nbDemand, 
                        names=colname_C)    
    
    # CV(v) - total distance cost for vehicle v
    colname_CV = [f'CV{v}' for v in range(nbSupply)]
    model.variables.add(obj=[1.0] * nbSupply, 
                        lb=[0.0] * nbSupply, 
                        ub=[cplex.infinity] * nbSupply, 
                        names=colname_CV)  
        
    # T(i) - Arrival time of vehicle at node i
    colname_T = [f'T{i}' for i in range(nbDemand)]
    model.variables.add(obj=[0.0] * nbDemand, 
                        lb=data['time_matrix'][0], 
                        ub=[cplex.infinity] * nbDemand, 
                        names=colname_T)
    
    # TV(v) - Tour Duration for each vehicle v
    colname_TV = [f'TV{v}' for v in range(nbSupply)]
    model.variables.add(obj=[labour_c] * nbSupply, 
                        lb=[0.0] * nbSupply, 
                        ub=[cplex.infinity] * nbSupply, 
                        names=colname_TV)  
    
    """Constraints"""
    
    # No 2 - DONE
    
    # for 
    # index = [0]
    # for j in range(nbSupply):
    #     # for i in range(nbDepot-1, nbDemand):
    #         #index[0] = i
    #     # index.append(i)
    #     print(len(colname_Y))
    #     lhs = colname_Y[j*(nbDemand-1):(j+1)*(nbDemand-1)]
    #     val = [1.0] * len(lhs)
    #     print(cplex.SparsePair(val, lhs))
    #     model.linear_constraints.add(lin_expr=cplex.SparsePair(val, lhs),
    #                                  senses="E", 
    #                                  rhs=[1.0])
    
    # No 3 - DONE
    index = [0]
    for v in range(nbSupply):
        index[0] = v
        val = [1.0] * nbDepot
        lhs = [[index[0], i] for i in val]
        model.linear_constraints.add(lin_expr=lhs,
                                      senses="L", 
                                      rhs=[1.0])   
    
    # # No 4 - DONE
    # index = []
    # for p in range(nbDepot):
    #     for v in range(nbSupply):
    #         for i in range(nbDepot+1, nbDemand): # First nbDepot 'nodes' are depots
    #             index.append(lngvarindex(p, v, i))
    #             print(p, i, data['distance_matrix'][p[0]][i])
    #             val = [-1.0] * nbDemand \
    #                 + [data['distance_matrix'][p][i]] * nbSupply \
    #                 + [data['distance_matrix'][p][i]] * nbSupply
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                           senses="G", 
    #                                           rhs=[data['distance_matrix'][p][i]])
                
    # # No 5a - DONE
    # index = []
    # for v in range(nbSupply):
    #     for i in range(1, nbDemand):
    #         for j in range(i+1,nbDemand):
    #             index.append(varindex(v,i))
    #             val = [1.0] * (nbDemand - i) \
    #                 + [-1.0] * nbDemand \
    #                 + [-M] * nbDemand * (nbDemand - i) \
    #                 + [-M] * nbSupply * nbDemand \
    #                 + [-M] * nbSupply * (nbDemand - i)
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                          senses='G',
    #                                          rhs= [[data['distance_matrix'][i][j]]*nbSupply \
    #                                                 + [-3*M]])
                
    # # No 5b - DONE
    # index = []
    # for v in range(nbSupply):
    #     for i in range(1, nbDemand):
    #         for j in range(i+1,nbDemand):
    #             index.append(varindex(v,i))
    #             val = [1.0] * nbDemand \
    #                 + [-1.0] * (nbDemand - i) \
    #                 + [M] * (nbDemand * (nbDemand - i)) \
    #                 + [-M] * nbSupply * nbDemand \
    #                 + [-M] * nbSupply * (nbDemand - i)
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                          senses='G',
    #                                          rhs=[[data['distance_matrix'][j][i]]*nbSupply \
    #                                                 + [-2*M]])
    # # No 6 - DONE
    # index = []
    # for p in range(nbDepot):
    #     for v in range(nbSupply):
    #         for i in range(p, nbDemand):
    #             index.append(lngvarindex(p, v, i))
    #             val = [1.0] * nbSupply \
    #                 + [1.0] * nbDemand \
    #                 + [-M] * nbDepot * nbSupply \
    #                 + [-M] * nbDemand * nbSupply
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                          senses='G',
    #                                          rhs=[[data['distance_matrix'][i][p]]*nbSupply \
    #                                                 + [-2*M]])
                    
    # # No 7 - DONE
    # index = []
    # for p in range(nbDepot):
    #     for v in range(nbSupply):
    #         for i in range(p, nbDemand):   
    #             index.append(lngvarindex(p, v, i))
    #             val = [1.0] * nbDemand \
    #                 + [-data['time_matrix'][p][i]] * nbSupply \
    #                 + [-data['time_matrix'][p][i]] * nbSupply
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                          senses='G',
    #                                          rhs=[[-data['time_matrix'][p][i]] * nbSupply])
                                             
    # # No 8a - 
    # index = []
    # for v in range(nbSupply):
    #     for i in range(1, nbDemand):
    #         for j in range(i+1,nbDemand):
    #             index.append(varindex(v, i))
    #             val = [1.0] * (nbDemand - i) \
    #                 + [-1.0] * nbDemand \
    #                 + [-M] * nbDemand * (nbDemand-i) \
    #                 + [-M] * nbSupply * nbDemand \
    #                 + [-M] * nbSupply * (nbDemand-i)
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                           senses='G',
    #                                           #st(i), but what?
    #                                           rhs = [data['time_matrix'][i][j] * nbSupply \
    #                                                  + [-3*M]])
                
    # # No 8b - 
    # index = []
    # for v in range(nbSupply):
    #     for i in range(1, nbDemand):
    #         for j in range(i+1,nbDemand):
    #             index.append(varindex(v, i))
    #             val = [-1.0] * (nbDemand - i) \
    #                 + [1.0] * nbDemand \
    #                 + [M] * nbDemand * (nbDemand-i) \
    #                 + [-M] * nbSupply * nbDemand \
    #                 + [-M] * nbSupply * (nbDemand-i)
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                           senses='G',
    #                                           #st(i), but what?
    #                                           rhs=[data['time_matrix'][j][i] * nbSupply \
    #                                                 + [-2*M]])

    # # No 9 - 
    # index = []
    # for p in range(nbDepot):
    #     for v in range(nbSupply):
    #         for i in range(p, nbDemand):
    #             index.append(lngvarindex(p, v, i))
    #             val = [1.0] * nbSupply \
    #                 + [-1.0] * nbDemand \
    #                 + [-M] * nbDepot * nbSupply \
    #                 + [-M] * nbDemand * nbSupply
    #             lhs = [[index, val]]
    #             model.linear_constraints.add(lin_expr=lhs,
    #                                           senses='G',
    #                                           #st(i), but what?
    #                                           rhs=[data['time_matrix'][i][p] * nbSupply \
    #                                                 + [-2*M]])
                                                  
    # # No 10 - DONE
    # index = []
    # for i in range(nbDemand):
    #     index.append(i)
    #     lhs = [1.0] * nbDemand + [1.0] * nbDemand
    #     row = [[index, lhs]]
    #     model.linear_constraints.add(lin_expr=row, 
    #                                  senses='G', 
    #                                  rhs=[data['time_windows'][i][0]])    
                 
    # # No 11 - DONE
    # index = []
    # for i in range(nbDemand):
    #     index.append(i)
    #     lhs = [1.0] * nbDemand + [1.0] * nbDemand
    #     row = [[index, lhs]]
    #     model.linear_constraints.add(lin_expr=row,
    #                                  senses='L',
    #                                  rhs=[data['time_windows'][i][1]])
    # # No 12 - DONE
    # index = []
    # for v in range(nbSupply):
    #     index.append(v)
    #     val = [1.0] * nbSupply + [-1.0] * nbSupply
    #     lhs = [[index, val]]
    #     model.linear_constraints.add(lin_expr=lhs,
    #                                  senses='L',
    #                                  rhs = [data['max_work_time'][v]])
        
    # # No 13 - DONE
    # index = []
    # for v in range(nbSupply):
    #     index.append(v)
    #     val = [data['demands'][i] for i in range(nbDemand)] \
    #         + data['vehicle_capacities'][v] * nbDepot
    #     lhs = [[index, val]]
    #     model.linear_constraints.add(lin_expr=lhs,
    #                                  senses='L',
    #                                  rhs = [0.0])

    # Solve Model
    model.solve()
    model.write("Transport_Problem.lp")
    
    
if __name__ == "__main__":
    model()