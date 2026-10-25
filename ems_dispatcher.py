import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.animation as animation
import matplotlib.lines as mlines
import random
import folium
import webbrowser
import os
from database_handler import DatabaseHandler

BG_COLOR = "#1e293b"
PANEL_COLOR = "#334155"
TEXT_COLOR = "#f1f5f9"
ROAD_COLOR = "#475569"
PATH_COLOR = "#60a5fa"
ACCIDENT_COLOR = "#f87171"
CONST_COLOR = "#fbbf24"
WEATHER_COLOR = "#38bdf8"
START_COLOR = "#4ade80"
END_COLOR = "#f43f5e"

class EMSDispatcher:
    def __init__(self):
        self.city_map = nx.Graph()
        self.ambulances = {
            "Unit 1": "Dispatch Base",
            "Unit 2": "Industrial Park",
            "Unit 3": "Highway A"
        }
        self.destination = "Crash Site"
        self.current_path = None
        self._build_city_network()

    def _build_city_network(self):
        intersections = {
            "Dispatch Base": (0, 4),
            "North Junction": (2, 6),
            "Uptown": (4, 7),
            "West Side": (2, 3),
            "City Center": (4, 4),
            "East Side": (7, 4),
            "Industrial Park": (3, 1),
            "South Junction": (5, 1),
            "Highway A": (7, 7),
            "Crash Site": (8, 2)
        }
        
        for name, pos in intersections.items():
            self.city_map.add_node(name, pos=pos)

        roads = [
            ("Dispatch Base", "North Junction", 4),
            ("Dispatch Base", "West Side", 3),
            ("North Junction", "Uptown", 5),
            ("North Junction", "City Center", 4),
            ("West Side", "City Center", 3),
            ("West Side", "Industrial Park", 5),
            ("Uptown", "City Center", 3),
            ("Uptown", "Highway A", 6),
            ("City Center", "East Side", 4),
            ("City Center", "South Junction", 5),
            ("Industrial Park", "South Junction", 4),
            ("South Junction", "Crash Site", 6),
            ("East Side", "Crash Site", 5),
            ("East Side", "Highway A", 4),
            ("Highway A", "Crash Site", 7)
        ]

        for u, v, base_time in roads:
            self.city_map.add_edge(u, v, base_time=base_time, current_time=base_time, status="Clear")

    def reset_network(self):
        for u, v in self.city_map.edges():
            self.city_map[u][v]['current_time'] = self.city_map[u][v]['base_time']
            self.city_map[u][v]['status'] = "Clear"

    def simulate_weather(self, condition="Heavy Rain"):
        multiplier = 1.5 if condition == "Heavy Rain" else 2.5 
        for u, v in self.city_map.edges():
            if self.city_map[u][v]['status'] == "Clear":
                self.city_map[u][v]['current_time'] = int(self.city_map[u][v]['base_time'] * multiplier)
                self.city_map[u][v]['status'] = condition

    def simulate_accident(self, node_a, node_b):
        if self.city_map.has_edge(node_a, node_b):
            self.city_map[node_a][node_b]['current_time'] += 45 
            self.city_map[node_a][node_b]['status'] = "MAJOR ACCIDENT"

    def simulate_construction(self, node_a, node_b):
        if self.city_map.has_edge(node_a, node_b):
            self.city_map[node_a][node_b]['current_time'] += 15
            self.city_map[node_a][node_b]['status'] = "CONSTRUCTION"

    def _heuristic(self, node1, node2):
        x1, y1 = self.city_map.nodes[node1]['pos']
        x2, y2 = self.city_map.nodes[node2]['pos']
        return abs(x1 - x2) + abs(y1 - y2)

    def penalty_weight(self, u, v, d):
        cost = d['current_time']
        if v in ["City Center", "North Junction", "South Junction"]:
            cost += 2 
        return cost

    def calculate_best_dispatch(self, end):
        best_path = None
        best_time = float('inf')
        best_unit = None
        
        for unit, start in self.ambulances.items():
            try:
                path = nx.astar_path(
                    self.city_map, source=start, target=end, 
                    heuristic=self._heuristic, weight=self.penalty_weight
                )
                time_cost = nx.astar_path_length(
                    self.city_map, source=start, target=end, 
                    heuristic=self._heuristic, weight=self.penalty_weight
                )
                if time_cost < best_time:
                    best_time = time_cost
                    best_path = path
                    best_unit = unit
            except nx.NetworkXNoPath:
                continue
                
        self.current_path = best_path
        return best_unit, best_path, best_time

    def generate_html_map(self):
        base_lat, base_lon = 30.767, 76.788
        coords = {node: (base_lat + pos[1]*0.005, base_lon + pos[0]*0.005) for node, pos in nx.get_node_attributes(self.city_map, 'pos').items()}
        
        m = folium.Map(
            location=[base_lat+0.02, base_lon+0.02], 
            zoom_start=14, 
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
            attr="Esri"
        )
        
        for u, v in self.city_map.edges():
            status = self.city_map[u][v]['status']
            color = "gray"
            weight = 2
            if status == "MAJOR ACCIDENT": color, weight = "red", 5
            elif status == "CONSTRUCTION": color, weight = "orange", 5
            
            folium.PolyLine([coords[u], coords[v]], color=color, weight=weight, opacity=0.7).add_to(m)

        for unit, start in self.ambulances.items():
            folium.Marker(coords[start], popup=unit, icon=folium.Icon(color='green', icon='plus')).add_to(m)
        folium.Marker(coords[self.destination], popup="Crash Site", icon=folium.Icon(color='red', icon='warning')).add_to(m)

        if self.current_path:
            path_coords = [coords[n] for n in self.current_path]
            folium.PolyLine(path_coords, color="#3b82f6", weight=6, opacity=0.9).add_to(m)
            
        m.save("live_dispatch_map.html")
        webbrowser.open('file://' + os.path.realpath('live_dispatch_map.html'))

    def plot_network_on_axis(self, ax, path, total_time, best_unit, latest_event):
        pos = nx.get_node_attributes(self.city_map, 'pos')
        ax.set_facecolor(BG_COLOR)
        ax.set_title("EMS Command: Multi-Agent Dispatch & Penalty Heuristic", fontsize=15, fontweight='bold', color=TEXT_COLOR, pad=20)

        edge_colors = []
        edge_widths = []
        for u, v in self.city_map.edges():
            status = self.city_map[u][v]['status']
            if status == "MAJOR ACCIDENT":
                edge_colors.append(ACCIDENT_COLOR); edge_widths.append(4)
            elif status == "CONSTRUCTION":
                edge_colors.append(CONST_COLOR); edge_widths.append(4)
            elif status in ["Heavy Rain", "Blizzard"]:
                edge_colors.append(WEATHER_COLOR); edge_widths.append(3)
            else:
                edge_colors.append(ROAD_COLOR); edge_widths.append(2)

        nx.draw_networkx_edges(self.city_map, pos, ax=ax, edge_color=edge_colors, width=edge_widths, alpha=0.9)
        nx.draw_networkx_nodes(self.city_map, pos, ax=ax, node_size=600, node_color=PANEL_COLOR, edgecolors=ROAD_COLOR)
        
        for unit, start in self.ambulances.items():
            nx.draw_networkx_nodes(self.city_map, pos, ax=ax, nodelist=[start], node_size=700, node_color=START_COLOR, edgecolors=BG_COLOR)
            
        nx.draw_networkx_nodes(self.city_map, pos, ax=ax, nodelist=[self.destination], node_size=700, node_color=END_COLOR, edgecolors=BG_COLOR)

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.city_map, pos, ax=ax, edgelist=path_edges, width=6, edge_color=PATH_COLOR, alpha=0.8)

        nx.draw_networkx_labels(self.city_map, pos, ax=ax, font_size=9, font_weight='bold', font_color=TEXT_COLOR)
        
        edge_labels = {(u, v): f"{d['current_time']}m" for u, v, d in self.city_map.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.city_map, pos, ax=ax, edge_labels=edge_labels, font_size=8, font_color=TEXT_COLOR,
            bbox=dict(facecolor=BG_COLOR, edgecolor='none', alpha=0.8)
        )

        ax.set_xlim(-1.5, 10)  
        ax.set_ylim(0, 8.5)    

        delay = total_time - 15
        delay_text = f" (+{delay}m anomaly)" if delay > 0 else " (Optimal)"
        
        info_text = f"DISPATCHED: {best_unit}\nETA: {total_time} mins{delay_text}\nEVENT: {latest_event}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                fontsize=11, fontweight='bold', color=TEXT_COLOR, verticalalignment='top', 
                bbox=dict(facecolor=PANEL_COLOR, alpha=0.9, edgecolor=ROAD_COLOR))

        legend_elements = [
            mlines.Line2D([], [], color=PATH_COLOR, linewidth=6, alpha=0.8, label='Optimal A* Route'),
            mlines.Line2D([], [], color=ACCIDENT_COLOR, linewidth=4, label='Major Accident (+45m)'),
            mlines.Line2D([], [], color=CONST_COLOR, linewidth=4, label='Construction (+15m)'),
            mlines.Line2D([], [], marker='o', color='w', markerfacecolor=START_COLOR, markersize=10, label='Available EMS Units')
        ]
        
        legend = ax.legend(handles=legend_elements, loc='lower right', facecolor=PANEL_COLOR, edgecolor=ROAD_COLOR)
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)
            
        ax.axis('off')

if __name__ == "__main__":
    dispatcher = EMSDispatcher()
    db = DatabaseHandler()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG_COLOR)  
    fig.canvas.manager.set_window_title('EMS Dispatch Optimizer')
    plt.subplots_adjust(bottom=0.15) 

    best_unit, path, time_cost = dispatcher.calculate_best_dispatch(dispatcher.destination)
    dispatcher.plot_network_on_axis(ax, path, time_cost, best_unit, "System Initialized.")

    ax_button = plt.axes([0.3, 0.03, 0.2, 0.075]) 
    btn = Button(ax_button, 'Start Auto-Sim (5s)', color=PANEL_COLOR, hovercolor=START_COLOR)
    btn.label.set_color(TEXT_COLOR)
    btn.label.set_fontweight('bold')
    
    ax_map_btn = plt.axes([0.55, 0.03, 0.2, 0.075])
    btn_map = Button(ax_map_btn, 'Export HTML Map', color=PANEL_COLOR, hovercolor=PATH_COLOR)
    btn_map.label.set_color(TEXT_COLOR)
    btn_map.label.set_fontweight('bold')
    
    is_simulating = [False] 

    def toggle_sim(event):
        is_simulating[0] = not is_simulating[0]
        if is_simulating[0]:
            btn.label.set_text('Stop Auto-Sim')
            btn.color = ACCIDENT_COLOR
        else:
            btn.label.set_text('Start Auto-Sim (5s)')
            btn.color = PANEL_COLOR
            
    def export_html(event):
        dispatcher.generate_html_map()

    btn.on_clicked(toggle_sim)
    btn_map.on_clicked(export_html)

    def update_frame(frame):
        if not is_simulating[0]:
            return 
            
        dispatcher.reset_network()
        
        possible_destinations = [node for node in dispatcher.city_map.nodes() if node not in dispatcher.ambulances.values()]
        dispatcher.destination = random.choice(possible_destinations)
        
        event_type = random.choice(["Weather", "Accident", "Accident", "Construction", "Construction"])
        latest_event = ""
        location_str = "Global Network"
        
        if event_type == "Weather":
            cond = random.choice(["Heavy Rain", "Blizzard"])
            dispatcher.simulate_weather(cond)
            latest_event = f"Weather: {cond} | Emergency: {dispatcher.destination}"
        else:
            edges = list(dispatcher.city_map.edges())
            u, v = random.choice(edges)
                
            location_str = f"{u} to {v}"
            if event_type == "Accident":
                dispatcher.simulate_accident(u, v)
                latest_event = f"Accident: {location_str} | Emergency: {dispatcher.destination}"
            else:
                dispatcher.simulate_construction(u, v)
                latest_event = f"Construction: {location_str} | Emergency: {dispatcher.destination}"
                
        best_unit, path, time_cost = dispatcher.calculate_best_dispatch(dispatcher.destination)
        
        db.log_dispatch(event_type, location_str, 15, time_cost)
        
        ax.clear() 
        dispatcher.plot_network_on_axis(ax, path, time_cost, best_unit, latest_event)

    ani = animation.FuncAnimation(fig, update_frame, interval=5000, cache_frame_data=False)
    plt.show()