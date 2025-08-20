import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
from shapely.geometry import LineString
from heapq import *
from collections import defaultdict
import math

def calculate_distance(pa, pb):  # Calculate distance between two points
    lat1, lon1 = pa
    lat2, lon2 = pb
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    try: return math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)) * 6371000
    except ValueError: return 0

def get_traffic_color(level):
    colors = [
        (1, (0, 255, 0)),    # Mức 1: Xanh lá 
        (3, (255, 255, 0)),  # Mức 3: Vàng 
        (5, (255, 165, 0)),  # Mức 5: Cam 
        (7, (255, 0, 0))     # Mức 7: Đỏ 
    ]
    
    for i in range(len(colors) - 1):
        level_start, (r_start, g_start, b_start) = colors[i]
        level_end, (r_end, g_end, b_end) = colors[i + 1]
        
        if level_start <= level <= level_end:
            ratio = (level - level_start) / (level_end - level_start)
            r = int(r_start + (r_end - r_start) * ratio)
            g = int(g_start + (g_end - g_start) * ratio)
            b = int(b_start + (b_end - b_start) * ratio)
            return f'#{r:02x}{g:02x}{b:02x}'
    
    return '#00FF00'

def geocode_address(address):
    try:
        geocode_result = ox.geocode(address)
        return (geocode_result[0], geocode_result[1])
    except:
        return None

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

# Function to load or create the graph
@st.cache_resource
def load_graph():
    G = ox.load_graphml(GRAPHML_FILE)
    graph = defaultdict(list)
    for edge in G.edges(data=True):
        graph[edge[0]].append((edge[1], edge[2]['length']))
        graph[edge[1]].append((edge[0], edge[2]['length']))
    nodes = dict()
    for node in G.nodes(data=True):
        nodes[node[0]] = (node[1]['y'], node[1]['x'])
    return G, graph, nodes

G, graph, nodes = load_graph()

# Khởi tạo session state
if 'points' not in st.session_state:
    st.session_state['points'] = []
if 'zoom' not in st.session_state:
    st.session_state['zoom'] = DEFAULT_ZOOM
if 'center' not in st.session_state:
    st.session_state['center'] = DEFAULT_LOCATION
if 'traffic_cache' not in st.session_state:
    st.session_state['traffic_cache'] = {}  # Khởi tạo traffic_cache
if 'edit_traffic_mode' not in st.session_state:
    st.session_state['edit_traffic_mode'] = False
if 'traffic_points' not in st.session_state:
    st.session_state['traffic_points'] = []
if 'temp_traffic_level' not in st.session_state:
    st.session_state['temp_traffic_level'] = 1
if 'traffic_click_mode' not in st.session_state:
    st.session_state['traffic_click_mode'] = False  # Trạng thái cho chế độ nhấp chuột

m = folium.Map(
    location=st.session_state['center'],
    zoom_start=st.session_state['zoom'],
    tiles='OpenStreetMap',
)

# Lựa chọn phương tiện
vehicle_type = st.sidebar.selectbox(
    "Chọn phương tiện:",
    ("Đi bộ", "Xe máy", "Ô tô")
)

# Thiết lập tốc độ theo phương tiện
if vehicle_type == "Đi bộ":
    speed_mps = 1.2  # ~4.3 km/h
elif vehicle_type == "Xe máy":
    speed_mps = 8.3  # ~30 km/h
else:
    speed_mps = 5.5  # ~20 km/h
if 'edge_modifier' not in st.session_state:
    st.session_state['edge_modifier'] = defaultdict(lambda: 1)
from copy import deepcopy
def Astar_algorithm(pointA, pointB, time_based=False, editing=False):
    global graph, nodes
    queue = []
    heappush(queue, (0, pointA))
    father = defaultdict(int)
    father[pointA] = -432
    res = defaultdict(int)
    res[pointA] = 0
    res[pointB] = 100000000  # Đặt giá trị mặc định cho điểm đích
    while queue:
        current_cost, current_node = heappop(queue)
        if current_node == pointB:
            break
        for neighbor, cost in graph[current_node]:
            coeff = deepcopy(st.session_state['edge_modifier'][(min(current_node, neighbor), max(current_node, neighbor))])
            #print(cost)
            if editing: coeff=1
            if coeff < 0: continue  # Tránh đoạn đường có chi phí âm
            if time_based==False: coeff = 1
            g = res[current_node] + cost * coeff
            h = calculate_distance(nodes[neighbor], nodes[pointB])
            f = g + h
            if neighbor not in father or f < res[neighbor] + h:
                heappush(queue, (f, neighbor))
                father[neighbor] = current_node
                res[neighbor] = g
    distance = res[pointB]
    if distance == 100000000:
        return 100000000, []
    path = []
    while father[pointB] != -432:
        path.append(pointB)
        pointB = father[pointB]
    path.append(pointA)
    path.reverse()
    return distance, path


for idx, point in enumerate(st.session_state['points']):
    folium.Marker(location=point, tooltip=f"Point {idx+1}", icon=folium.Icon("blue")).add_to(m)

if len(st.session_state['points']) == 2:
    orig = st.session_state['points'][0]
    dest = st.session_state['points'][1]
    orig_node = ox.nearest_nodes(G, orig[1], orig[0])
    dest_node = ox.nearest_nodes(G, dest[1], dest[0])
    distance, route = Astar_algorithm(orig_node, dest_node,time_based=False,editing=False)
    if distance==100000000 or not route:
        st.sidebar.markdown("Không tìm thấy đường đi.");
    else:
        dis2,route2 = Astar_algorithm(dest_node, orig_node, time_based=True,editing=False)
        #caculate actual distance in route2
        actual_distance = 0
        for u, v in zip(route2[:-1], route2[1:]):
            print(st.session_state['edge_modifier'][(min(u, v), max(u, v))])
            data = G.get_edge_data(u, v)
            if data:
                edge_data = data[list(data.keys())[0]]
                if 'length' in edge_data:
                    actual_distance += edge_data['length']
        dis1=0
        for u, v in zip(route[:-1], route[1:]):
            print(st.session_state['edge_modifier'][(min(u, v), max(u, v))])

            data = G.get_edge_data(u, v)
            if data:
                edge_data = data[list(data.keys())[0]]
                if 'length' in edge_data:
                    dis1 += edge_data['length']*st.session_state['edge_modifier'][(min(u, v), max(u, v))]
        distance_km = distance 
        from math import ceil
        time_seconds = ceil(dis1 / speed_mps)
        quickest_time_seconds = ceil(dis2 / speed_mps)
        st.sidebar.markdown("### Kết quả tìm đường")
        st.sidebar.markdown(f"- **Phương tiện**: `{vehicle_type}`")

        st.sidebar.markdown(f"1.Quãng đường ngắn nhất:")
        st.sidebar.markdown(f"- **Khoảng cách**: `{distance:.1f}` mét")
        st.sidebar.markdown(f"- **Thời gian ước tính**: `{time_seconds}` giây")
        st.sidebar.markdown(f"2.Quãng đường nhanh nhất:")
        st.sidebar.markdown(f"- **Khoảng cách**: `{actual_distance:.1f}` mét")
        st.sidebar.markdown(f"- **Thời gian ước tính**: `{quickest_time_seconds}` giây")
        edge_geometries = []
        for u, v in zip(route[:-1], route[1:]):
            data = G.get_edge_data(u, v)
            if data:
                edge_data = data[list(data.keys())[0]]
                if 'geometry' in edge_data:
                    edge_geometries.append(edge_data['geometry'])
                else:
                    point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
                    point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
                    edge_geometries.append(LineString([point_u, point_v]))
        for geom in edge_geometries:
            coords = [(lat, lon) for lon, lat in geom.coords]
            folium.PolyLine(coords, color='blue', tooltip="Too much smoothing?", weight=3).add_to(m)
        edge_geometries = []
        for u, v in zip(route2[:-1], route2[1:]):
        
            data = G.get_edge_data(u, v)
            if data:
                edge_data = data[list(data.keys())[0]]
                if 'geometry' in edge_data:
                    edge_geometries.append(edge_data['geometry'])
                else:
                    point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
                    point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
                    edge_geometries.append(LineString([point_u, point_v]))
        for geom in edge_geometries:
            coords = [(lat, lon) for lon, lat in geom.coords]
            folium.PolyLine(coords, color='green', tooltip="Too much smoothing?", weight=3).add_to(m)

def get_traffic_status(segment):
    for u, v in zip(segment[:-1], segment[1:]):
        edge_key = tuple(sorted([u, v]))
        if edge_key in st.session_state['traffic_cache']:
            return st.session_state['traffic_cache'][edge_key]
    return 1  # Mặc định mức 1 nếu không tìm thấy


st.title("Phương Mai District Map")

# Chức năng chỉnh độ tắc đường
st.sidebar.title("Chỉnh độ tắc đường")
if st.sidebar.button("Bắt đầu chỉnh độ tắc đường"):
    st.session_state['edit_traffic_mode'] = True
    st.session_state['traffic_points'] = []
    st.session_state['temp_traffic_level'] = 1
    st.session_state['traffic_click_mode'] = 1
    st.rerun()
traffic_scale=[0, 1, 1.5, 2, 2.5, 3, 4, -1]  # Tỷ lệ tắc đường từ 1 đến 7
if st.session_state['edit_traffic_mode']:
    traffic_level = st.sidebar.slider(
        "Mức độ tắc đường",
        min_value=1,
        max_value=7,
        value=st.session_state.get('temp_traffic_level', 1),
        step=1,
        help="1: Thông thoáng (xanh lá), 3: Bình thường (vàng), 5: Tắc nghẽn (cam), 7: Cấm đường (đỏ)"
    )
    st.session_state['temp_traffic_level'] = traffic_level
    #css tí kcg đâu
    st.sidebar.markdown(
        f"""
        <style>
        div[data-testid="stSlider"] > div {{
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 10px;
        }}
        div[role="slider"] > div {{
            display: none !important;
        }}
        div[role="slider"] > div:hover {{
            transform: scale(1.2);
        }}
        div[data-testid="stSlider"] .thumb {{
            background: linear-gradient(to right, #00FF00, #FFFF00, #FFA500, #FF0000);
            height: 6px;
            border-radius: 3px;
        }}
        div[data-testid="stSlider"]::after {{
            content: '{traffic_level}';
            display: block;
            text-align: center;
            margin-top: 5px;
            font-weight: bold;
            color: black;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if len(st.session_state.get('traffic_points', [])) == 2:
        orig = st.session_state['traffic_points'][0]
        dest = st.session_state['traffic_points'][1]
        folium.Marker(location=orig, tooltip="Điểm đầu", icon=folium.Icon("blue")).add_to(m)
        folium.Marker(location=dest, tooltip="Điểm cuối", icon=folium.Icon("blue")).add_to(m)
        orig_node = ox.nearest_nodes(G, orig[1], orig[0])
        dest_node = ox.nearest_nodes(G, dest[1], dest[0])
        _, route = Astar_algorithm(orig_node, dest_node, editing=True)
        
        for u, v in zip(route[:-1], route[1:]):
            st.session_state['edge_modifier'][(min(u, v), max(u, v))] = traffic_scale[traffic_level]
            data = G.get_edge_data(u, v)
            if data:
                edge_data = data[list(data.keys())[0]]
                if 'geometry' in edge_data:
                    geom = edge_data['geometry']
                    coords = [(lat, lon) for lon, lat in geom.coords]
                else:
                    point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
                    point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
                    coords = [(point_u[1], point_u[0]), (point_v[1], point_v[0])]
                display_color = get_traffic_color(traffic_level)
                folium.PolyLine(
                    coords,
                    color=display_color,
                    weight=5,
                    opacity=0.8,
                    tooltip=f"Mức tắc đường: {traffic_level}"
                ).add_to(m)
                edge_key = tuple(sorted([u, v]))
                st.session_state.traffic_cache[edge_key] = traffic_level
        if st.sidebar.button("Update"):
            st.session_state['edit_traffic_mode'] = False
            st.session_state['traffic_points'] = []
            st.session_state['traffic_click_mode'] = False
            st.rerun()

output = st_folium(m, width=1000, height=500, returned_objects=['last_clicked', 'zoom', 'center'])

# nhấp chuột
if output and output['last_clicked']:
    clicked_point = (output['last_clicked']['lat'], output['last_clicked']['lng'])
    st.session_state['zoom'] = output['zoom']
    st.session_state['center'] = output['center']['lat'], output['center']['lng']
    if st.session_state['edit_traffic_mode'] and st.session_state['traffic_click_mode'] and len(st.session_state['traffic_points']) < 2:
        if clicked_point not in st.session_state['traffic_points']:
            st.session_state['traffic_points'].append(clicked_point)
            folium.Marker(
                location=clicked_point,
                tooltip=f"Điểm {'đầu' if len(st.session_state['traffic_points']) == 1 else 'cuối'}",
                icon=folium.Icon("blue")
            ).add_to(m)
            st.rerun()
    elif not st.session_state['edit_traffic_mode'] and len(st.session_state['points']) < 2:
        st.session_state['points'].append(clicked_point)
        st.rerun()

if st.button("Reset Points"):
    st.session_state['points'] = []
    st.session_state['zoom'] = DEFAULT_ZOOM
    st.session_state['center'] = DEFAULT_LOCATION
    st.rerun()

st.sidebar.title("Nhập địa chỉ: ")

start_address = st.sidebar.text_input("Điểm xuất phát")
end_address = st.sidebar.text_input("Điểm đến")
if st.sidebar.button("Đặt lại tắt đường"):
    st.session_state['traffic_cache'] = {}
    st.session_state['edge_modifier'] = defaultdict(lambda: 1)
    st.session_state['edit_traffic_mode'] = False
    st.session_state['traffic_points'] = []
    st.session_state['temp_traffic_level'] = 1
    st.session_state['traffic_click_mode'] = False
    st.rerun()
if st.sidebar.button("Tìm đường"):
    if start_address and end_address:
        start_point = geocode_address(start_address)
        end_point = geocode_address(end_address)
        if start_point and end_point:
            st.session_state['points'] = [start_point, end_point]
            st.session_state['center'] = start_point
            st.session_state['zoom'] = 16
            st.rerun()
        else:
            st.sidebar.error("Không thể tìm thấy một trong các địa chỉ.")
    else:
        st.sidebar.warning("Vui lòng nhập cả điểm xuất phát và điểm đến.")