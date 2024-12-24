from cluster import clustering
from create_data import create_data_model

import json
FILE = r'./data.json'

def load_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':

    data = create_data_model()
    print("Num v", data["num_vehicles"])
    DV=False
    print(f"Allow dummy vehicles = {DV}\n")  
    clusters = clustering(data, dummy_vehicles=DV)
    for i, cluster in enumerate(clusters):
        print(f"Cluster {i+1}: ")
        print(f"Nodes: {cluster}\n")