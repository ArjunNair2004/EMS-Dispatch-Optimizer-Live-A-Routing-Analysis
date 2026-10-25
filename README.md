# EMS-Dispatch-Optimizer-Live-A-Routing-Analysis
A Python-based optimization engine that simulates a real-time Emergency Medical Services (EMS) dispatch grid. This project demonstrates advanced Graph Theory and dynamic pathfinding by using the A (A-Star) Search Algorithm* to instantly reroute an ambulance around dynamic city hazards (traffic, accidents, and weather).

🧠 Core Algorithms & Data Structures
Graph Theory: The city is modeled as an undirected weighted graph where Nodes represent intersections and Edges represent roads.

A Search Algorithm:* Calculates the optimal route by evaluating both the real-world edge weight (current_time) and a geographic Heuristic (Manhattan Distance to the target).

Dynamic Edge Weighting: Road weights are not static. The network actively listens for simulated API events and adjusts edge costs on the fly.

Heuristic Optimization: Uses spatial (x, y) coordinate tracking to bias the algorithm's search path toward the physical location of the crash site, making it significantly faster than standard Dijkstra's.

✨ Key Features
The "Chaos Engine" (Auto-Sim): An automated event injector that triggers a new hazard every 5 seconds. It intelligently targets roads currently on the ambulance's route to force algorithmic rerouting.

Live Detour Calculation: Instantly calculates the new ETA and displays the exact time penalty (e.g., +2m detour) caused by rerouting around a blocked main artery.

Hazard Simulations:

🛑 Major Accidents: Adds +45 minutes (Forces immediate reroute).

🚧 Construction Zones: Adds +15 minutes (Algorithm evaluates if a detour is actually faster).

🌧️ Weather Degradation: Global multipliers (Heavy Rain or Blizzard) that scale the cost of all edges simultaneously.

Professional Dashboard: Built with Matplotlib using a low-glare "Dark Slate" telemetry UI, complete with live event logs and an interactive legend.

🛠️ Technology Stack
Python 3.x

NetworkX: Industry-standard library for complex network/graph mathematical operations.

Matplotlib: Used for rendering the interactive, 60-FPS updating telemetry dashboard and analytical graph drawing.

## 🚀 How to Run the Project

### Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### Step-by-Step Installation

**1. Clone the repository:**
Open your terminal and download the project files:
bash
git clone [https://github.com/ArjunNair2004/EMS-Dispatch-Optimizer-Live-A-Routing-Analysis.git](https://github.com/ArjunNair2004/EMS-Dispatch-Optimizer-Live-A-Routing-Analysis.git)
cd EMS-Dispatch-Optimizer-Live-A-Routing-Analysis

2. Set up a Virtual Environment (Recommended):
Keep your dependencies isolated by creating a virtual environment.
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate

3. Install Dependencies:
The project relies on two primary data science libraries.
pip install networkx matplotlib

Execution
Run the optimization engine from your terminal:
python ems_dashboard.py

🎮 How to Use the Dashboard
Observe the Initial State: The application will launch a Dark Slate UI window showing the optimal 15-minute baseline route.

Engage the Chaos Engine: Click the Start Auto-Sim (5s) button located at the bottom of the window.

Analyze the Visual Rerouting: Every 5 seconds, the engine will deliberately target the ambulance's intended path with a random hazard (Accident, Construction, or Weather). Watch the A* algorithm instantly recalculate and snap the blue path to the fastest available detour.

Monitor the Terminal Logs: Keep your command line visible! The backend engine prints a live dispatch manifest to the console detailing the exact hazard spawned and the resulting ETA recalculation.
