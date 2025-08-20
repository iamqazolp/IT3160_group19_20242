'''Hướng dẫn sử dụng:
Có 2 chế độ vẽ: (Khởi đầu mặc định là vẽ đỉnh)
1. Vẽ đỉnh
Trong vẽ đỉnh có 2 chế độ con: nối cạnh và không nối cạnh
-Nối cạnh: đặt 1 đỉnh mới sẽ nối với đỉnh gần nhất (mặc định)
-Không nối cạnh: đặt 1 đỉnh mới sẽ không nối với đỉnh gần nhất
Đổi chế độ bằng cách nhấn phím "g"
2. Vẽ cạnh
Trong vẽ cạnh có 2 chế độ con: ghim và nối lần lượt
- Ghim: double click vào 1 đỉnh sẽ ghim đỉnh đó lại, sau đó click vào đỉnh khác sẽ nối 2 đỉnh đó lại
- Nối lần lượt: click lần lượt vào 2 đỉnh sẽ nối 2 đỉnh đó lại (mặc định)
muốn ghim thì double click vào đỉnh đó, muốn bỏ ghim thì double click vào góc màn hình hoặc 1 chỗ trống nào đó k gần các đỉnh khác
Đổi chế độ bằng cách nhấn chuột phải 1 lần. Khi đổi chế độ thì sẽ chuyển sang chế độ con mặc định của chế độ đó
Ctrl +Z để undo 
Ctrl + S để save lại trạng thái hiện tại của đồ thị vào file "saved_graph.txt"
Nguyên tắc vẽ: đặt đỉnh tại các giao lộ, trên đường cong thì đặt nhiều đỉnh để nối đường cong đó, 1 cạnh không được quá dài
(ví dụ đoạn giải phóng khá dài thì cần chia thanh nhiều đoạn ngắn để nối lại với nhau)'''
import tkinter as tk
from collections import defaultdict
from PIL import Image, ImageTk
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(2)
MAX_DISTANCE_SQ = 900

class GraphEditorApp:
    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title("Map Viewer")
        
        # Initialize state variables
        self.node_mode = 0
        self.edge_mode = 0
        self.pin_mode = 0
        self.selected_nodes = []
        self.nodes = []
        self.edges = []
        self.events_list = []
        self.event_des = []
        
        # Setup GUI
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        self._setup_canvas()
        self._bind_events()
        self.load_graph()
        
        self.root.mainloop()

    def _setup_canvas(self):
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Double-Button-1>", self.toggle_pin_mode)
        self.canvas.bind("<Button-3>", self.switch_edge_mode)
        self.canvas.bind("g", self.switch_node_mode)
        self.root.bind("<Control-s>", self.save_graph)
        self.root.bind("<Control-z>", self.undo_action)
        self.canvas.focus_set()

    def switch_node_mode(self, event):
        self.node_mode = (self.node_mode + 1) % 2

    def switch_edge_mode(self, event):
        self.edge_mode = (self.edge_mode + 1) % 2
        self.pin_mode = 0
        self.selected_nodes.clear()

    def toggle_pin_mode(self, event):
        if self.edge_mode:
            x, y = event.x, event.y
            nearest = self._find_nearest_node(x, y)
            
            if nearest and self._calculate_distance_sq(nearest, (x, y)) <= MAX_DISTANCE_SQ:
                self.selected_nodes = [nearest]
            else:
                self.selected_nodes.clear()

    def handle_click(self, event):
        if self.edge_mode:
            self._handle_edge_click(event)
        else:
            self._handle_node_click(event)

    def _handle_node_click(self, event):
        x, y = event.x, event.y
        self.nodes.append((x, y))
        self._draw_node(x, y)

        if self.node_mode == 0 and len(self.nodes) > 1:
            prev = self._find_nearest_node(x, y, last=True)
            self._draw_edge(prev, (x, y))

    def _handle_edge_click(self, event):
        x, y = event.x, event.y
        nearest = self._find_nearest_node(x, y)
        
        if nearest and self._calculate_distance_sq(nearest, (x, y)) <= MAX_DISTANCE_SQ:
            self.selected_nodes.append(nearest)
            
            if len(self.selected_nodes) == 2:
                self._draw_edge(*self.selected_nodes)
                if self.pin_mode:
                    self.selected_nodes.pop(0)
                else:
                    self.selected_nodes.clear()

    def _find_nearest_node(self, x, y, last=False):
        if not self.nodes:
            return None
        if last:
            return min(self.nodes[:-1], key=lambda n: self._calculate_distance_sq(n, (x, y)))
        return min(self.nodes, key=lambda n: self._calculate_distance_sq(n, (x, y)))

    def _draw_node(self, x, y):
        r = 5
        oval = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill='red')
        self.events_list.append(oval)
        self.event_des.append(f"o {x} {y}\n")

    def _draw_edge(self, start, end):
        line = self.canvas.create_line(*start, *end, fill='blue')
        self.events_list.append(line)
        self.event_des.append(f"l {start[0]} {start[1]} {end[0]} {end[1]}\n")
        self.edges.extend([(start, end), (end, start)])

    def undo_action(self, event):
        if self.events_list:
            canvas_id = self.events_list.pop()
            self.canvas.delete(canvas_id)
            if self.event_des[-1].startswith('o'):
                self.nodes.pop()
            else:
                self.edges = self.edges[:-2]
            self.event_des.pop()

    def save_graph(self, event):
        with open("saved_graph.txt", "w") as f:
            f.writelines(self.event_des)

    def load_graph(self):
        try:
            with open("saved_graph.txt", "r") as f:
                for line in f:
                    if line.startswith('o'):
                        x, y = map(int, line.split()[1:])
                        self._draw_node(x, y)
                        self.nodes.append((x, y))
                    elif line.startswith('l'):
                        coords = list(map(int, line.split()[1:]))
                        self._draw_edge((coords[0], coords[1]), (coords[2], coords[3]))
        except FileNotFoundError:
            pass

    @staticmethod
    def _calculate_distance_sq(p1, p2):
        return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

if __name__ == "__main__":
    GraphEditorApp("ss.png")