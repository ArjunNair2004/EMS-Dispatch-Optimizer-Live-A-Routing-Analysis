import customtkinter as ctk
import sqlite3

class AnalyticsWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EMS Analytics Dashboard")
        self.geometry("450x350")
        
        self.label = ctk.CTkLabel(self, text="Performance Analytics", font=("Arial", 22, "bold"))
        self.label.pack(pady=20)
        
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect("ems_logs.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM dispatch_logs")
            total_dispatches = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(time_saved) FROM dispatch_logs")
            total_time_saved = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT hazard_type, COUNT(*) FROM dispatch_logs GROUP BY hazard_type")
            hazard_counts = cursor.fetchall()
            
            conn.close()

            ctk.CTkLabel(self.stats_frame, text=f"Total Dynamic Reroutes: {total_dispatches}", font=("Arial", 16)).pack(pady=10)
            ctk.CTkLabel(self.stats_frame, text=f"Total Time Saved: {total_time_saved} minutes", font=("Arial", 16, "bold"), text_color="#4ade80").pack(pady=10)
            
            ctk.CTkLabel(self.stats_frame, text="Hazard Breakdown:", font=("Arial", 14, "underline")).pack(pady=10)
            for hazard, count in hazard_counts:
                ctk.CTkLabel(self.stats_frame, text=f"- {hazard}: {count} bypasses").pack()

        except Exception:
            ctk.CTkLabel(self.stats_frame, text="No database found. Run simulation first.", text_color="red").pack(pady=20)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = AnalyticsWindow()
    app.mainloop()