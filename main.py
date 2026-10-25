import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
import matplotlib.lines as mlines
from ems_dispatcher import EMSDispatcher
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

class EMSCommandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMS Dispatch Command - Auth")
        self.root.geometry("500x450")
        self.root.configure(bg=BG_COLOR)
        
        self.dispatcher = EMSDispatcher()
        self.db = DatabaseHandler()
        
        self.create_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_window()
        self.root.title("EMS Dispatch Command - Auth")
        
        title = tk.Label(self.root, text="EMS Dispatcher Login", font=("Arial", 22, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title.pack(pady=40)

        self.user_entry = tk.Entry(self.root, font=("Arial", 14), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, justify="center")
        self.user_entry.insert(0, "admin")
        self.user_entry.pack(pady=15, ipadx=10, ipady=8)

        self.pass_entry = tk.Entry(self.root, font=("Arial", 14), show="*", bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, justify="center")
        self.pass_entry.insert(0, "admin123")
        self.pass_entry.pack(pady=15, ipadx=10, ipady=8)

        login_btn = tk.Button(self.root, text="Login", font=("Arial", 12, "bold"), bg="#2563eb", fg=TEXT_COLOR, width=15, bd=0, command=self.verify_login)
        login_btn.pack(pady=20, ipady=8)

    def verify_login(self):
        if self.user_entry.get() == "admin" and self.pass_entry.get() == "admin123":
            self.create_main_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials. Use admin / admin123")

    def create_main_menu(self):
        self.clear_window()
        self.root.title("EMS Dispatch Command - Main Menu")
        
        title = tk.Label(self.root, text="Main Menu", font=("Arial", 24, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title.pack(pady=60)

        sim_btn = tk.Button(self.root, text="Launch Live Simulation", font=("Arial", 12, "bold"), bg="#2563eb", fg=TEXT_COLOR, width=22, bd=0, command=self.open_simulation_window)
        sim_btn.pack(pady=15, ipady=10)

        analytics_btn = tk.Button(self.root, text="View Analytics", font=("Arial", 12, "bold"), bg="#10b981", fg=TEXT_COLOR, width=22, bd=0, command=self.open_analytics_window)
        analytics_btn.pack(pady=15, ipady=10)

    def open_simulation_window(self):
        sim_win = tk.Toplevel(self.root)
        sim_win.title("EMS Dispatch Optimizer")
        sim_win.geometry("1100x850")
        sim_win.configure(bg=BG_COLOR)

        fig, ax = plt.subplots(figsize=(11, 7))
        fig.patch.set_facecolor(BG_COLOR)
        plt.subplots_adjust(bottom=0.15)

        best_unit, path, time_cost = self.dispatcher.calculate_best_dispatch(self.dispatcher.destination)
        self.dispatcher.plot_network_on_axis(ax, path, time_cost, best_unit, "System Initialized.")

        canvas = FigureCanvasTkAgg(fig, master=sim_win)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        is_simulating = [False]

        def toggle_sim():
            is_simulating[0] = not is_simulating[0]
            if is_simulating[0]:
                btn_sim.config(text="Stop Auto-Sim", bg=ACCIDENT_COLOR)
                run_auto_sim()
            else:
                btn_sim.config(text="Start Auto-Sim (5s)", bg=PANEL_COLOR)

        def run_auto_sim():
            if not is_simulating[0]:
                return
            
            self.dispatcher.reset_network()
            possible_destinations = [n for n in self.dispatcher.city_map.nodes() if n not in self.dispatcher.ambulances.values()]
            self.dispatcher.destination = random.choice(possible_destinations)
            
            event_type = random.choice(["Weather", "Accident", "Accident", "Construction", "Construction"])
            latest_event = ""
            location_str = "Global Network"
            
            if event_type == "Weather":
                cond = random.choice(["Heavy Rain", "Blizzard"])
                self.dispatcher.simulate_weather(cond)
                latest_event = f"Weather: {cond} | Emergency: {self.dispatcher.destination}"
            else:
                edges = list(self.dispatcher.city_map.edges())
                u, v = random.choice(edges)
                location_str = f"{u} to {v}"
                if event_type == "Accident":
                    self.dispatcher.simulate_accident(u, v)
                    latest_event = f"Accident: {location_str} | Emergency: {self.dispatcher.destination}"
                else:
                    self.dispatcher.simulate_construction(u, v)
                    latest_event = f"Construction: {location_str} | Emergency: {self.dispatcher.destination}"
                    
            best_unit, path, time_cost = self.dispatcher.calculate_best_dispatch(self.dispatcher.destination)
            self.db.log_dispatch(event_type, location_str, 15, time_cost)
            
            ax.clear()
            self.dispatcher.plot_network_on_axis(ax, path, time_cost, best_unit, latest_event)
            canvas.draw()
            
            sim_win.after(5000, run_auto_sim)

        def export_map():
            self.dispatcher.generate_html_map()
            messagebox.showinfo("Success", "Interactive HTML map exported and opened in browser!")

        btn_frame = tk.Frame(sim_win, bg=BG_COLOR)
        btn_frame.pack(side=tk.BOTTOM, pady=20)

        btn_sim = tk.Button(btn_frame, text="Start Auto-Sim (5s)", font=("Arial", 11, "bold"), bg=PANEL_COLOR, fg=TEXT_COLOR, width=20, bd=0, command=toggle_sim)
        btn_sim.pack(side=tk.LEFT, padx=15, ipady=8)

        btn_map = tk.Button(btn_frame, text="Export HTML Map", font=("Arial", 11, "bold"), bg=PANEL_COLOR, fg=TEXT_COLOR, width=20, bd=0, command=export_map)
        btn_map.pack(side=tk.LEFT, padx=15, ipady=8)

    def open_analytics_window(self):
        an_win = tk.Toplevel(self.root)
        an_win.title("EMS Analytics Dashboard")
        an_win.geometry("550x650")
        an_win.configure(bg=BG_COLOR)

        title = tk.Label(an_win, text="Performance Analytics", font=("Arial", 22, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title.pack(pady=25)

        card = tk.Frame(an_win, bg=PANEL_COLOR, bd=0)
        card.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = sqlite3.connect("ems_logs.db")
            c = conn.cursor()
            c.execute("SELECT COUNT(*), SUM(time_saved) FROM dispatch_logs")
            total_reroutes, time_saved = c.fetchone()
            c.execute("SELECT hazard_type, COUNT(*) FROM dispatch_logs GROUP BY hazard_type")
            hazards = dict(c.fetchall())
            conn.close()
        except:
            total_reroutes, time_saved, hazards = 0, 0, {}

        tk.Label(card, text=f"Total Dynamic Reroutes: {total_reroutes or 0}", font=("Arial", 16, "bold"), fg=TEXT_COLOR, bg=PANEL_COLOR).pack(pady=20)
        tk.Label(card, text=f"Total Time Saved: {time_saved or 0} minutes", font=("Arial", 16, "bold"), fg=START_COLOR, bg=PANEL_COLOR).pack(pady=10)

        tk.Label(card, text="Hazard Breakdown:", font=("Arial", 14, "underline"), fg=TEXT_COLOR, bg=PANEL_COLOR).pack(pady=15)
        
        for h_type, count in hazards.items():
            tk.Label(card, text=f"- {h_type}: {count} bypasses", font=("Arial", 13), fg=TEXT_COLOR, bg=PANEL_COLOR).pack(anchor="w", padx=60, pady=2)

        def export_csv():
            self.db.export_to_csv()
            messagebox.showinfo("Success", "Data exported to CSV successfully!")

        def clear_db():
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all logs?"):
                self.db.clear_database()
                messagebox.showinfo("Success", "Database cleared!")
                an_win.destroy()
                self.open_analytics_window()

        btn_csv = tk.Button(an_win, text="Export Data to CSV", font=("Arial", 11, "bold"), bg="#6366f1", fg=TEXT_COLOR, width=25, bd=0, command=export_csv)
        btn_csv.pack(pady=15, ipady=8)

        btn_clear = tk.Button(an_win, text="Clear Database", font=("Arial", 11, "bold"), bg="#ef4444", fg=TEXT_COLOR, width=25, bd=0, command=clear_db)
        btn_clear.pack(pady=5, ipady=8)

if __name__ == "__main__":
    root = tk.Tk()
    app = EMSCommandApp(root)
    root.mainloop()