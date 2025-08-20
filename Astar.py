
import osmnx as ox
from heapq import *
def calculate_distance(pa,pb): # Calculate distance between two points
    from math import radians, sin, cos, sqrt, atan2, acos
    lat1, lon1 = pa
    lat2, lon2 = pb
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    return acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371000

# Configure OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 300
CENTER_LAT = 21.00285
CENTER_LON = 105.84084 
ZOOM_START = 16
DEFAULT_LOCATION = (CENTER_LAT, CENTER_LON) #location of Phuong Mai, Dong Da, Hanoi, Vietnam
DEFAULT_ZOOM = ZOOM_START
# Define the path to the saved graph file
GRAPHML_FILE = "phuongmai.graphml"

# Function to load or create the graph

from collections import defaultdict

G = ox.load_graphml(GRAPHML_FILE)


graph = defaultdict(list)
for edge in G.edges(data=True):
    graph[edge[0]].append((edge[1], edge[2]['length']))
    graph[edge[1]].append((edge[0], edge[2]['length']))
nodes = dict()
for node in G.nodes(data=True):
    nodes[node[0]] = (node[1]['y'],node[1]['x'])
from heapq import *
from collections import defaultdict
def Astar_algorithm(pointA, pointB):
    global graph, nodes
    queue = []
    heappush(queue, (0, pointA))
    father = defaultdict(int)
    father[pointA] = -432
    res = defaultdict(int)
    res[pointA] = 0
    while queue:
        current_cost, current_node = heappop(queue)
        if current_node == pointB:
            break
        for neighbor, cost in graph[current_node]:
            g = current_cost + cost
            h = calculate_distance(nodes[neighbor], nodes[pointB])
            f = g + h
            if neighbor not in father or f < res[neighbor]:
                heappush(queue, (f, neighbor))
                father[neighbor] = current_node
                res[neighbor] = f
                print(f)
    distance = res[pointB]
    path = []
    while father[pointB] != -432:
        path.append(pointB)
        pointB = father[pointB]
    path.append(pointA)
    path.reverse()
    print(distance)
    print(path)
    return distance, path
Astar_algorithm(5721823832,9339541983)
'''5721823832 9339541983
[5721823832, 5721823830, 6406043750, 8277275742, 10000094724867, 8277275727, 10000066675416, 10000010052310, 10000021324501, 10000005595859, 10000007430865, 10000073753291, 8277275724, 10000074277577, 8277275739, 10000054878551, 5721877144, 12222035149, 8277275728, 10000043868933, 10000006906634, 10130399567, 6661539805, 2294884824, 10130399534, 10000097084443, 10000095511579, 10000064054288, 10000071918607, 10000050947086, 10000023421962, 10000020276233, 10000043082760, 10000079782920, 10000007431170, 10000086598659, 10000009004034, 9439560362, 10000060384285, 9439560364, 10000026043430, 10000093152297, 10000030499885, 12223911406, 5716457440, 9339541983]'''