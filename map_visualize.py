import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx
import os
from shapely.geometry import LineString

# Configure OSMnx
ox.config(use_cache=True, log_console=False)

# Define the default center location and zoom level
DEFAULT_CENTER = [21.00285, 105.84084]
DEFAULT_ZOOM = 16

# Define the path to the saved graph file
GRAPHML_FILE = "hanoi_drive.graphml"

# Function to load or create the graph
@st.cache_resource
def load_graph():
    if os.path.exists(GRAPHML_FILE):
        G = ox.load_graphml(GRAPHML_FILE)
    else:
        G = ox.graph_from_point((DEFAULT_CENTER[0], DEFAULT_CENTER[1]), dist=2000, network_type='drive')
        ox.save_graphml(G, GRAPHML_FILE)
    return G

# Load the graph
G = load_graph()

# Initialize session state for storing clicked points, zoom, and center
if 'points' not in st.session_state:
    st.session_state['points'] = []
if 'zoom' not in st.session_state:
    st.session_state['zoom'] = DEFAULT_ZOOM
if 'center' not in st.session_state:
    st.session_state['center'] = DEFAULT_CENTER

# Create a Folium map with stored zoom and center
m = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles='cartodbpositron')

# Add existing markers to the map
for idx, point in enumerate(st.session_state['points']):
    folium.Marker(location=point, tooltip=f"Point {idx+1}").add_to(m)

# If two points are selected, compute and display the shortest path
if len(st.session_state['points']) == 2:
    orig = st.session_state['points'][0]
    dest = st.session_state['points'][1]

    # Find the nearest nodes in the graph
    orig_node = ox.nearest_nodes(G, orig[1], orig[0])
    dest_node = ox.nearest_nodes(G, dest[1], dest[0])

    # Compute the shortest path
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    # Extract the edge geometries for the route
    edge_geometries = []
    for u, v in zip(route[:-1], route[1:]):
        data = G.get_edge_data(u, v)
        print("__________________________")
        print(data)
        print("__________________________")
        if data:
            # If multiple edges exist between two nodes, choose the first one
            edge_data = data[list(data.keys())[0]]
            print("*****************")
            print(edge_data)
            print("*****************")
            if 'geometry' in edge_data:
                # If geometry is available, use it
                edge_geometries.append(edge_data['geometry'])
            else:
                # If no geometry, create a straight line between nodes
                point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
                point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
                edge_geometries.append(LineString([point_u, point_v]))

    # Plot the route on the map using the edge geometries
    for geom in edge_geometries:
        coords = [(lat, lon) for lon, lat in geom.coords]
        folium.PolyLine(coords, color='red', weight=4).add_to(m)

# Display the map and capture click events
output = st_folium(m, width=700, height=500)

# Update session state with current zoom and center
if output:
    if 'zoom' in output:
        st.session_state['zoom'] = output['zoom']
    if 'center' in output:
        st.session_state['center'] = output['center']

# Handle map clicks
if output and output['last_clicked']:
    clicked_point = (output['last_clicked']['lat'], output['last_clicked']['lng'])
    if len(st.session_state['points']) < 2:
        st.session_state['points'].append(clicked_point)
        st.rerun()

# Add a button to reset the selected points
if st.button("Reset Points"):
    st.session_state['points'] = []
    st.rerun()
