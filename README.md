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
