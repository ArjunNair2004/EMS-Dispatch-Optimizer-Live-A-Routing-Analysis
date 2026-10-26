# EMS Dispatch Optimizer: Live A* Routing Analysis

A Python desktop simulation of an Emergency Medical Services (EMS) dispatch centre. The city is modelled as a weighted graph, and the **A\* search algorithm** chooses the fastest ambulance and route for an emergency. Accidents, construction and bad weather are injected at random, so the system has to **re-route in real time**. Every dispatch is logged to SQLite for analytics and CSV export.

> This is an academic simulation. It uses a small synthetic road network, not real map data, and it is not connected to live traffic, GPS or real emergency services.

---

## Features

- **Multi-agent dispatch:** compares three ambulance units and dispatches the one with the lowest travel cost.
- **A\* pathfinding:** Manhattan-distance heuristic plus a custom edge-penalty function (built on NetworkX).
- **Dynamic hazards:** accidents, construction zones and weather change road travel times and force re-routing.
- **Auto-simulation:** a new random emergency and hazard every 5 seconds.
- **Two visualisations:**
  - a live Matplotlib network view embedded in the Tkinter window
  - an interactive Folium HTML map with dark tiles
- **Login and menu:** a simple admin login leading to the simulation and analytics windows.
- **SQLite analytics:** total reroutes, estimated time saved and a breakdown by hazard type, with CSV export and a clear-logs option.

---

## How It Works

### 1. The city graph
The network has **10 intersections** and **15 roads**. Each road has a base travel time in minutes.

| Intersection | Grid position |
|---|---|
| Dispatch Base | (0, 4) |
| North Junction | (2, 6) |
| Uptown | (4, 7) |
| West Side | (2, 3) |
| City Center | (4, 4) |
| East Side | (7, 4) |
| Industrial Park | (3, 1) |
| South Junction | (5, 1) |
| Highway A | (7, 7) |
| Crash Site | (8, 2) |

Three ambulance units wait at fixed bases:

| Unit | Base |
|---|---|
| Unit 1 | Dispatch Base |
| Unit 2 | Industrial Park |
| Unit 3 | Highway A |

### 2. Choosing the best ambulance
For each unit, A* finds the cheapest route from its base to the emergency. The unit with the lowest total cost is dispatched.

- **Heuristic:** Manhattan distance between node coordinates, `|x1 - x2| + |y1 - y2|`.
- **Edge cost:** the road's current travel time, plus **+2 minutes** when entering a congested hub (City Center, North Junction or South Junction).
- Every road's base time is at least the Manhattan distance between its endpoints, and hazards only add cost, so the heuristic never overestimates and the routes are optimal for the modelled graph.

### 3. Hazards
At the start of each cycle the network is reset to base conditions, then one random event is applied.

| Event | Chance | Effect |
|---|---|---|
| Accident | 40% | +45 min on one random road (red) |
| Construction | 40% | +15 min on one random road (amber) |
| Weather | 20% | Heavy Rain: `int(base x 1.5)`, or Blizzard: `int(base x 2.5)`, on all clear roads (light blue) |

### 4. The simulation loop
Every 5 seconds the app:

1. resets the network
2. picks a random destination (any intersection that is not an ambulance base)
3. injects a random hazard
4. runs A* for every unit and selects the best
5. redraws the network and logs the event to SQLite

### 5. Logging and time saved
Each dispatch is stored in the `dispatch_logs` table. "Time saved" is an estimate against a nominal 15-minute ETA:

```
time_saved = (15 + hazard_penalty) - detour_eta
hazard_penalty = 45 (Accident), 15 (Construction), 10 (Weather)
```

---

## Screens

| Screen | What it does |
|---|---|
| Login | Admin sign-in (credentials below) |
| Main Menu | Launch Live Simulation or View Analytics |
| Simulation | Colour-coded roads, optimal route, dispatched unit, ETA and event text; Start/Stop Auto-Sim and Export HTML Map buttons |
| HTML Map | Folium map with ambulance bases, crash site, hazards and route |
| Analytics | Total reroutes, total time saved, hazard breakdown; Export CSV and Clear Database |

---

## Project Structure

```
.
├── main.py                  # Tkinter app: login, menu, simulation and analytics windows
├── ems_dispatcher.py        # EMSDispatcher: graph, A* dispatch, hazards, Matplotlib plot, Folium map
├── database_handler.py      # DatabaseHandler: create table, log dispatch, export CSV, clear
├── analytics.py             # Standalone CustomTkinter analytics window (not used by main.py)
├── ems_logs.db              # SQLite database
├── ems_dispatch_report.csv  # Exported log
├── live_dispatch_map.html   # Generated interactive map
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Database

SQLite file `ems_logs.db`, table `dispatch_logs`:

| Column | Type | Description |
|---|---|---|
| dispatch_id | INTEGER (PK, autoincrement) | Record id |
| timestamp | TEXT | `YYYY-MM-DD HH:MM:SS` |
| hazard_type | TEXT | Weather / Accident / Construction |
| location | TEXT | Affected road ("A to B") or "Global Network" for weather |
| base_eta | INTEGER | Nominal ETA (15) |
| detour_eta | INTEGER | ETA after re-routing |
| time_saved | INTEGER | Estimated minutes saved |

CSV export columns: `Dispatch ID, Timestamp, Hazard Type, Location, Base ETA, Detour ETA, Time Saved`.

---

## Getting Started

### Prerequisites
- Python 3.10 or newer, with Tkinter (included with most Python installers)
- A modern web browser for the HTML map

### Install
```bash
pip install networkx matplotlib folium
```
`customtkinter` is only needed if you want to run the standalone `analytics.py`:
```bash
pip install customtkinter
```

### Run
```bash
python main.py
```

### Login
| Username | Password |
|---|---|
| `admin` | `admin123` |

### Usage
1. Sign in and choose **Launch Live Simulation**.
2. Click **Start Auto-Sim (5s)** to begin generating emergencies and hazards.
3. Click **Export HTML Map** to open the interactive map in your browser.
4. Close the simulation and choose **View Analytics** to see reroutes, time saved and the hazard breakdown.
5. Use **Export Data to CSV** or **Clear Database** as needed.

---

## Limitations

- The road network is a small synthetic graph, not real road data.
- Hazards are random and replace one another each cycle.
- "Time saved" is an estimate against a fixed 15-minute baseline.
- The login is hard-coded (`admin` / `admin123`) and meant for local demos only.
- No live traffic, GPS, patient priority or ambulance availability.
- No automated tests.

## Future Work

- Load real road graphs (OpenStreetMap / OSMnx) and use real coordinates.
- Integrate live traffic and weather APIs.
- Track ambulances in real time, with busy/available states.
- Handle incident priority, hospital selection and multiple simultaneous emergencies.
- Hashed passwords and role-based access.
- Migrate to a server database (for example Oracle with PL/SQL procedures).
- Charts in the analytics view and unit tests.

---

## Technologies

Python, NetworkX, Matplotlib, Tkinter, Folium (Leaflet), SQLite (`sqlite3`), CustomTkinter (optional).

## Author

Arjun Nair, MCA, University Institute of Computing, Chandigarh University.
