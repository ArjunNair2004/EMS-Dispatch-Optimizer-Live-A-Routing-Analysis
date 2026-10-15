import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.animation as animation
import matplotlib.lines as mlines
import random

# --- SOFT DARK THEME COLORS ---
BG_COLOR = "#1e293b"       # Soft dark slate background
PANEL_COLOR = "#334155"    # Slightly lighter slate for nodes and UI boxes
TEXT_COLOR = "#f1f5f9"     # Off-white for readable text
ROAD_COLOR = "#475569"     # Muted gray for normal roads
PATH_COLOR = "#60a5fa"     # Soft bright blue for the optimal route
ACCIDENT_COLOR = "#f87171" # Soft red
CONST_COLOR = "#fbbf24"    # Soft amber
WEATHER_COLOR = "#38bdf8"  # Soft sky blue
START_COLOR = "#4ade80"    # Soft green
END_COLOR = "#f43f5e"      # Soft rose

class EMSDispatcher:
    def __init__(self):
        self.city_map = nx.Graph()
        self.source = "Dispatch Base"
        self.destination = "Crash Site"
        self._build_city_network()

    def _build_city_network(self):
        """Constructs the Network with base travel times and physical coordinates."""
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

        # All roads start clear
        for u, v, base_time in roads:
            self.city_map.add_edge(u, v, base_time=base_time, current_time=base_time, status="Clear")

    def reset_network(self):
        """Clears all traffic and weather anomalies back to perfect conditions."""
        for u, v in self.city_map.edges():
            self.city_map[u][v]['current_time'] = self.city_map[u][v]['base_time']
            self.city_map[u][v]['status'] = "Clear"

    # --- SIMULATION INJECTORS ---
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

    # --- A* PATHFINDING ALGORITHM ---
    def _heuristic(self, node1, node2):
        x1, y1 = self.city_map.nodes[node1]['pos']
        x2, y2 = self.city_map.nodes[node2]['pos']
        return abs(x1 - x2) + abs(y1 - y2)

    def calculate_optimal_route(self, start, end):
        try:
            path = nx.astar_path(
                self.city_map, source=start, target=end, 
                heuristic=self._heuristic, weight='current_time'
            )
            total_time = nx.astar_path_length(
                self.city_map, source=start, target=end, 
                heuristic=self._heuristic, weight='current_time'
            )
            return path, total_time
        except nx.NetworkXNoPath:
            return None, float('inf')

    # --- VISUALIZATION ---
    def plot_network_on_axis(self, ax, path, total_time, latest_event):
        """Draws the analytical network onto the provided matplotlib axis."""
        pos = nx.get_node_attributes(self.city_map, 'pos')
        
        # Ensure the background color stays consistent after clearing
        ax.set_facecolor(BG_COLOR)
        
        # Title with padding to prevent overlap
        ax.set_title("EMS Command: Live A* Routing Analysis", 
                     fontsize=15, fontweight='bold', color=TEXT_COLOR, pad=20)

        # Map edge colors based on their current status
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

        # Draw the base graph components
        nx.draw_networkx_edges(self.city_map, pos, ax=ax, edge_color=edge_colors, width=edge_widths, alpha=0.9)
        nx.draw_networkx_nodes(self.city_map, pos, ax=ax, node_size=600, node_color=PANEL_COLOR, edgecolors=ROAD_COLOR)
        
        # Highlight Start and End points
        nx.draw_networkx_nodes(self.city_map, pos, ax=ax, nodelist=[self.source], node_size=700, node_color=START_COLOR, edgecolors=BG_COLOR)
        nx.draw_networkx_nodes(self.city_map, pos, ax=ax, nodelist=[self.destination], node_size=700, node_color=END_COLOR, edgecolors=BG_COLOR)

        # Draw Optimal Path
        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.city_map, pos, ax=ax, edgelist=path_edges, width=6, edge_color=PATH_COLOR, alpha=0.8)

        # Draw Labels (Nodes and Edges)
        nx.draw_networkx_labels(self.city_map, pos, ax=ax, font_size=9, font_weight='bold', font_color=TEXT_COLOR)
        
        edge_labels = {(u, v): f"{d['current_time']}m" for u, v, d in self.city_map.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.city_map, pos, ax=ax, edge_labels=edge_labels, font_size=8, font_color=TEXT_COLOR,
            bbox=dict(facecolor=BG_COLOR, edgecolor='none', alpha=0.8)
        )

        # --- THE FIX: Expand the boundaries of the canvas to create UI margins ---
        ax.set_xlim(-1.5, 10)  # Pushes the left edge out, and gives a large right margin for the legend
        ax.set_ylim(0, 8.5)    # Pushes the top edge up so the HUD has empty space to sit in

        # Anchored Telemetry HUD Text
        info_text = f"ETA TO TARGET: {total_time} mins\nLATEST EVENT: {latest_event}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                fontsize=11, fontweight='bold', color=TEXT_COLOR, verticalalignment='top', 
                bbox=dict(facecolor=PANEL_COLOR, alpha=0.9, edgecolor=ROAD_COLOR))

        # Add Legend
        legend_elements = [
            mlines.Line2D([], [], color=PATH_COLOR, linewidth=6, alpha=0.8, label='Optimal A* Route'),
            mlines.Line2D([], [], color=ACCIDENT_COLOR, linewidth=4, label='Major Accident (+45m)'),
            mlines.Line2D([], [], color=CONST_COLOR, linewidth=4, label='Construction (+15m)'),
            mlines.Line2D([], [], color=WEATHER_COLOR, linewidth=3, label='Weather Degradation')
        ]
        
        # Style the legend to match the dark theme
        legend = ax.legend(handles=legend_elements, loc='lower right', facecolor=PANEL_COLOR, edgecolor=ROAD_COLOR)
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)
            
        ax.axis('off')


# ==========================================
# MAIN DASHBOARD LOOP & GUI
# ==========================================
if __name__ == "__main__":
    dispatcher = EMSDispatcher()
    
    # 1. Setup the UI Window
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG_COLOR)  
    fig.canvas.manager.set_window_title('EMS Dispatch Optimizer')
    plt.subplots_adjust(bottom=0.15) 

    # Initial Draw (Perfect conditions)
    path, time_cost = dispatcher.calculate_optimal_route(dispatcher.source, dispatcher.destination)
    dispatcher.plot_network_on_axis(ax, path, time_cost, "System Initialized. Awaiting simulation...")

    # 2. Setup the "Auto-Simulate" Button
    ax_button = plt.axes([0.4, 0.03, 0.2, 0.075]) 
    btn = Button(ax_button, 'Start Auto-Sim (5s)', color=PANEL_COLOR, hovercolor=START_COLOR)
    btn.label.set_color(TEXT_COLOR)
    btn.label.set_fontweight('bold')
    
    is_simulating = [False] 

    def toggle_sim(event):
        """Button Click Event Handler"""
        is_simulating[0] = not is_simulating[0]
        if is_simulating[0]:
            btn.label.set_text('Stop Auto-Sim')
            btn.color = ACCIDENT_COLOR
            print("\n[SYSTEM] Auto-Simulation Started...")
        else:
            btn.label.set_text('Start Auto-Sim (5s)')
            btn.color = PANEL_COLOR
            print("\n[SYSTEM] Auto-Simulation Paused.")
            
    btn.on_clicked(toggle_sim)

    # 3. Setup the 5-Second Animation Loop
    def update_frame(frame):
        if not is_simulating[0]:
            return 
            
        # Clear the old traffic
        dispatcher.reset_network()
        
        # --- SMART AI: Target the optimal path! ---
        default_path, _ = dispatcher.calculate_optimal_route(dispatcher.source, dispatcher.destination)
        
        event_type = random.choice(["Weather", "Accident", "Accident", "Construction", "Construction"])
        latest_event = ""
        
        if event_type == "Weather":
            cond = random.choice(["Heavy Rain", "Blizzard"])
            dispatcher.simulate_weather(cond)
            latest_event = f"Global Weather Pattern: {cond}"
        else:
            # Force a reroute by picking an edge directly off the default path
            if default_path and len(default_path) > 1:
                path_edges = list(zip(default_path, default_path[1:]))
                u, v = random.choice(path_edges)
            else:
                edges = list(dispatcher.city_map.edges())
                u, v = random.choice(edges)
                
            if event_type == "Accident":
                dispatcher.simulate_accident(u, v)
                latest_event = f"Major Accident Logged: {u} to {v}"
            else:
                dispatcher.simulate_construction(u, v)
                latest_event = f"Construction Zone: {u} to {v}"
                
        # Run A* AI and print the terminal report
        path, time_cost = dispatcher.calculate_optimal_route(dispatcher.source, dispatcher.destination)
        
        print(f">> NEW EVENT: {latest_event} | Re-routing... New ETA: {time_cost} mins")
        
        # Clear the old drawing and repaint the map
        ax.clear() 
        dispatcher.plot_network_on_axis(ax, path, time_cost, latest_event)

    ani = animation.FuncAnimation(fig, update_frame, interval=5000, cache_frame_data=False)
    plt.show()