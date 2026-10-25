# EMS Dispatch Optimizer

An advanced multi-agent emergency medical service (EMS) vehicle routing, simulation, and analytics command center built with Python, NetworkX, and Tkinter. The project implements a custom A* pathfinding algorithm featuring dynamic edge weighting, multi-unit ambulance assignment, real-time hazard injection (accidents, construction, and weather), and persistent performance analytics logging.

## Key Features & Architecture

- **Multi-Agent A* Pathfinding:** Evaluates the road network across Chandigarh using a custom heuristic with edge penalties. It calculates and dispatches the optimal ambulance unit from multiple base stations based on live travel costs.
- **Dynamic Hazard Simulation:** Automatically injects randomized events (accidents adding major delays, construction zones, and severe weather conditions) that dynamically alter edge weights and force real-time rerouting during auto-simulation cycles.
- **Secure Authentication & Menu Workflow:** Features a dedicated login interface (`admin` / `admin123`) leading to a main menu that toggles between live simulation and performance analytics windows.
- **Dual Visualizations:** 
  - Real-time Matplotlib-based simulation dashboard embedded directly inside the desktop application with auto-simulation controls.
  - Interactive HTML-based mapping powered by Folium and Esri Dark tiles, completely free of watermarks and API access errors.
- **SQLite Performance Analytics & Reporting:** Automatically tracks total dynamic reroutes, time saved, and hazard breakdowns (accidents, construction, weather bypasses), with built-in features to export logs to CSV or clear the database.

## Project Structure

```text
├── main_app.py           # Main Tkinter desktop application (Auth, Menu, Simulation, Analytics)
├── ems_dispatcher.py     # Core A* routing engine, graph setup, and map generation
├── database_handler.py   # SQLite database handler for logging metrics, CSV export, and clearing
└── ems_logs.db           # SQLite database for tracking dispatch performance history
Getting Started
Prerequisites
Ensure you have Python installed along with the required libraries:

Bash
pip install networkx matplotlib folium
Running the Application
Launch the desktop command application from the root directory:

Bash
python main_app.py
Login Credentials
Username: admin

Password: admin123
