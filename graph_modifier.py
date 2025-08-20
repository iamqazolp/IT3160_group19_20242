import osmnx as ox  
from shapely.geometry import LineString
from random import randint

random_id = [int(x) for x in open('random_id.txt').readlines()]

G=ox.graph_from_place("Phương Mai, Đống Đa, Hà Nội, Vietnam")
max_length = 6
nodes = dict()

cnt=0
for node in G.nodes(data=True):
    nodes[node[0]] = node[1]
def get_coordinates(node_id):
    node = G.nodes[node_id]
    return node['y'], node['x']
def calculate_distance(pa,pb):
    from math import radians, sin, cos, sqrt, atan2, acos
    lat1, lon1 = pa
    lat2, lon2 = pb
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    return acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371000
def add_edge(node1, node2):
    global G
    G.add_edge(node2,node1,length = calculate_distance(get_coordinates(node1),get_coordinates(node2)) ,oneway = False)
    G.add_edge(node1,node2,length = calculate_distance(get_coordinates(node1),get_coordinates(node2)) ,oneway = False)
def remove_edge(node1, node2):
    global G
    try: G.remove_edge(node1, node2)
    except Exception: pass
    try: G.remove_edge(node2, node1)
    except Exception: pass
e= '''10130399531-10130399532
10130399532-10130399533
10130399533-10130399534
10130399534-10130399535
10130399536-10130399535

10130399536-10130399577
10130399577-10130399578
10130399578-10130399537
10130399537-10130399538
10130399538-10130399550
10130399550-10130399539
10130399567-10130399568'''
for x in e.split('\n'):
    if not x.strip(): continue
    a,b = map(int,x.split('-'))
    remove_edge(a,b)
n='''
10130399571
10130399576
10130399579
10130399551
10130399573
10130399574
10130376693
10130399577
10130399550'''
for x in n.split('\n'):
    if not x.strip(): continue
    x = int(x.strip())
    try: G.remove_node(x)
    except Exception: pass
    try: del nodes[x]
    except Exception: pass
add_edge(10130399575,104782499)

def process_edge_linestring(edge):
    global G,cnt
    pa = nodes[edge[0]]['y'], nodes[edge[0]]['x']
    pb = nodes[edge[1]]['y'], nodes[edge[1]]['x']
    data = edge[2]
    one_way = data['oneway']
    if 'geometry' in data:
        G.remove_edge(edge[0], edge[1])
        l = [chunk for chunk in data['geometry'].coords]
        idx =[edge[0]]
        for i in range(1,len(l)-1):
            G.add_node(random_id[cnt], y=l[i][1], x=l[i][0])
            nodes[random_id[cnt]] = {'y':l[i][1],'x':l[i][0]}
            idx.append(random_id[cnt])
            G.add_edge(random_id[cnt],idx[-2],length=calculate_distance(l[i],l[i-1]),oneway = one_way)
            if one_way==False:
                G.add_edge(idx[-2],random_id[cnt],length=calculate_distance(l[i],l[i-1]),oneway = False)
            cnt+=1
        G.add_edge(edge[1],idx[-1],length=calculate_distance(l[-1],l[-2]), oneway = one_way)
        if one_way==False:
            G.add_edge(idx[-1],edge[1],length=calculate_distance(l[-1],l[-2]),oneway = False)
for node in G.nodes(data=True):
    nodes[node[0]] = node[1]
from copy import deepcopy

def process_long_edge(edge):
    global G,cnt
    pa = nodes[edge[0]]['y'], nodes[edge[0]]['x']
    pb = nodes[edge[1]]['y'], nodes[edge[1]]['x']
    data = edge[2]
    one_way = data['oneway']
    length=calculate_distance(pa,pb)
    if length<=2*max_length:
        return

    try: G.remove_edge(edge[0], edge[1])
    except Exception: return
    try: G.remove_edge(edge[1], edge[0])  #y,x
    except Exception: pass
    increment = max_length/length
    dy = (pb[0]-pa[0])*increment
    dx = (pb[1]-pa[1])*increment
    newnodes_id = [edge[0]]
    newnodes_coor = [pa]
    for i in range(1,int(length/max_length)):
        coor = (pa[0]+dy*i,pa[1]+dx*i)
    
        G.add_node(random_id[cnt], y=coor[0], x=coor[1])
        nodes[random_id[cnt]] = {'y':coor[0],'x':coor[1]}
        nodes[random_id[cnt]] = {'y':coor[0],'x':coor[1]}
        G.add_edge(random_id[cnt],newnodes_id[-1],length=calculate_distance(newnodes_coor[-1],coor),oneway = one_way)
        if one_way==False:
            G.add_edge(newnodes_id[-1],random_id[cnt],length=calculate_distance(newnodes_coor[-1],coor),oneway = False)
        newnodes_coor.append(coor)
        newnodes_id.append(random_id[cnt])
        cnt+=1
    G.add_edge(edge[1],newnodes_id[-1],length=calculate_distance(newnodes_coor[-1],pb), oneway = one_way)
    if one_way==False:  
        G.add_edge(newnodes_id[-1],edge[1],length=calculate_distance(newnodes_coor[-1],pb), oneway = False)
    newnodes_coor.append(pb)
    newnodes_id.append(edge[1])
for edge in deepcopy(G.edges(data=True)): 
    if edge[0]==10130399575 and edge[1]==104782499:
        print(43782532658675782)
        process_long_edge(edge)
add_edge(5721823832,10000081354761)
for edge in deepcopy(G.edges(data=True)):
    process_edge_linestring(edge)
for edge in deepcopy(G.edges(data=True)):
    process_long_edge(edge)
ox.save_graphml(G, "phuongmai.graphml") 
