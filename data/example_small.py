import json

def create_data_model():
    """Stores the data for the problem."""
    data = {}

    data['labour_cost'] = 1
    # Distance from node i to node j
    data['distance_matrix'] = [
        [
            0, 548, 776, 696, 582, 274, 502
        ],
        [
            548, 0, 684, 308, 194, 502, 730
        ],
        [
            776, 684, 0, 992, 878, 502, 274
        ],
        [
            696, 308, 992, 0, 114, 650, 878
        ],
        [
            582, 194, 878, 114, 0, 536, 764
        ],
        [
            274, 502, 502, 650, 536, 0, 228
        ],
        [
            502, 730, 274, 878, 764, 228, 0
        ],
    ]
    
    data['node_demands'] = [0, 1, 1, 2, 4, 2, 4]
    
    
    data['vehicle_capacities'] = [5, 15]
    data['fixed_vehicle_cost'] = [1, 1]

    # Counts of variables
    data['counts'] = {
        'depots': 1,
        'vehicles': len(data['vehicle_capacities']),
        'nodes': len(data['node_demands'])
    }

    # Generated data
    data['vehicle_T_penalty'] = [1.0] * data['counts']['vehicles']
    data['max_work_time'] = [8.0] * data['counts']['vehicles']
    data['service_time'] = [1 for i in range(data['counts']['nodes'])]
    data['node_T_penalty'] = [1.0] * data['counts']['nodes']

    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3, 6],
        [6, 0, 8, 3, 2, 6, 8],
        [9, 8, 0, 11, 10, 6, 3],
        [8, 3, 11, 0, 1, 7, 10],
        [7, 2, 10, 1, 0, 6, 9],
        [3, 6, 6, 7, 6, 0, 2],
        [6, 8, 3, 10, 9, 2, 0],
        [2, 4, 9, 6, 4, 3, 6],
        [3, 8, 5, 10, 8, 2, 2],
        [2, 8, 8, 10, 9, 2, 5],
        [6, 13, 4, 14, 13, 7, 4],
        [6, 7, 15, 6, 4, 9, 12],
        [4, 5, 14, 7, 6, 7, 10],
        [4, 8, 13, 9, 8, 7, 10],
        [5, 12, 9, 14, 12, 6, 6],
        [9, 10, 18, 6, 8, 12, 15],
        [7, 14, 9, 16, 14, 8, 5]
    ]
    data['time_windows'] = [ # tuples in form (a,b)
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10)
    ]
    
    return data