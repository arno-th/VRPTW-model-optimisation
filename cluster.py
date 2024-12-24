##############################################################################
# 
# @created: Oct 2023
# @author: Arno Theron
##############################################################################

import numpy as np

def clustering(data, dummy_vehicles):
    nbDepot = data['depot']
    nbDemand = len(data['demands'])
    C = []
    
    # Step 1(a)
    L = np.array([(i, data['time_windows'][i][0], data['time_windows'][i][1]) \
                     for i in range(nbDepot, nbDemand)],
                    dtype=[('index', int), ('ai', int), ('bi', int)])                
    L = np.sort(L, order=['ai', 'bi'])
    
    # Step 1(b)
    V = np.array([(i, data['vehicle_capacities'][i]/data['fixed_vehicle_cost'][i]) \
                  for i in range(data['num_vehicles'])],
                 dtype=[('index', int), ('ratio', float)])
    V = np.sort(V, order=['ratio'])[::-1]
    
    # Step 1(c)
    d_max = 1000
    delta = 0.5
    
    while len(L) > 0:
        # Checking for enough vehicles
        if len(C) >= data['num_vehicles'] and dummy_vehicles:
            data['num_vehicles'] += 1
            data['vehicle_capacities'].append(15)
            data['max_work_time'].append(8.0)
            data['fixed_vehicle_cost'].append(1)
        if len(C) >= data['num_vehicles'] and not dummy_vehicles:
            print('Not enough vehicles. Exiting with current clusters.')
            return C
            
        step = 2
        # Step 2-3(a)
        K=[L[0][0]]
        
        aC = data['time_windows'][K[0]][0]
        bC = data['time_windows'][K[0]][1]
        wC = data['demands'][K[0]]
        stC = data['service_time'][K[0]]
        
        # Step 3(b)
        L = np.delete(L, 0)
        L_prime = L
        
        # Step 4-6
        while len(L_prime) > 0:
            node_j = L_prime[0]
            # Step 4
            step = 4
            if wC + data['demands'][node_j[0]] <= data['vehicle_capacities'][len(C)]:
                
                # Step 5(a)
                d_min = data['distance_matrix'][node_j[0]][K[0]]
                for i in K:
                    d_ji = data['distance_matrix'][node_j[0]][i]
                    if d_ji <= d_min:
                        d_min = d_ji
                        node_i = i
                
                # Step 5(b)
                step = 5
                if d_ji <= d_max:
                    # Step 6
                    bj = node_j[2]
                    step = 6
                    if aC + stC + data['time_matrix'][node_j[0]][node_i] <= max(bC, bj):
                        # Step 7
                        step = 7
                        if aC + stC + data['time_matrix'][node_j[0]][node_i] \
                            + delta >= node_j[1]:
                                step = 8                           
                                # Step 8(a)
                                K.append(node_j[0])
                                wC += data['demands'][node_j[0]]
                                stC = max(stC + data['time_matrix'][node_j[0]][node_i] 
                                          + data['service_time'][node_j[0]], 
                                          node_j[1] + data['service_time'][node_j[0]] 
                                          - data['time_windows'][node_i][0])
                                
                                # Step 8(b)
                                if bC > node_j[2]:
                                    bC = node_j[2]
                                    
                                # node_j will be unique value as it has unique index No in its 0th index
                                L_prime = np.delete(L_prime, np.where(L_prime == node_j))
                                L = np.delete(L, np.where(L == node_j))
                                # print("L:", L)
                        else:        
                            L_prime = []
                            # print("C:", C)
                
            if len(L_prime) > 0:
                L_prime = np.delete(L_prime, 0)
        # Step 9
        # Prints last step before closing cluster
        #print("Step:", step)
        C.append(K)
        # print("C:", C)    
    return C
