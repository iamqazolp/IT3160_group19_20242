import osmnx as ox
import folium
import contextily as cx
import matplotlib.pyplot as plt
PLACE_NAME = 'Phương Mai, Đống Đa, Hà Nội, Vietnam'
G = ox.graph_from_place(PLACE_NAME)
nodes, edges = ox.graph_to_gdfs(G)

# Create a Folium map centered on the location
m = folium.Map(location=[21.00309, 105.83897], zoom_start=13, tiles='cartodbpositron')
for _, row in edges.iterrows():
    folium.PolyLine(locations=[(lat, lon) for lon, lat in row['geometry'].coords],
                    color='blue',
                    weight=2).add_to(m)

# Display the map
m.save("hanoi_map.html")