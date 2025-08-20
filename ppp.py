

import osmnx as ox
from shapely.geometry import LineString
from heapq import *
from collections import defaultdict
import math
import matplotlib.pyplot as plt
# Configure OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 300
CENTER_LAT = 21.00285
CENTER_LON = 105.84084 
ZOOM_START = 16
DEFAULT_LOCATION = (CENTER_LAT, CENTER_LON)  # location of Phuong Mai, Dong Da, Hanoi, Vietnam
DEFAULT_ZOOM = ZOOM_START
# Define the path to the saved graph file
GRAPHML_FILE = "phuongmai.graphml"

#        folium.Marker(location=orig, tooltip="Điểm đầu", icon=folium.Icon("blue")).add_to(m)

# Function to load or create the graph
G=ox.load_graphml(GRAPHML_FILE) 
print(len(G.nodes), len(G.edges))

