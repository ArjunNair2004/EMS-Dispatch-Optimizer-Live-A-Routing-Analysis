import customtkinter as ctk
import sqlite3
import csv

class AnalyticsWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EMS Analytics Dashboard")
        self.geometry("450x450")
        
        self.label = ctk.CTkLabel(self, text="Performance Analytics", font=("Arial", 22, "bold"))
        self.label.pack(pady=20)
        
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.load_data()
        
        self.export_btn = ctk.CTkButton(self, text="Export Data to CSV", command=self.export_csv, fg_color="#4f46e5", hover_color="#4338ca")
        self.export_btn.pack(pady=10)

        self.clear_btn = ctk.CTkButton(self, text="Clear Database", command=self.clear_db, fg_color="#ef4444", hover_color="#b91c1c")
        self.clear_btn.pack(pady=10)

    def load_data(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
            
        try:
            conn = sqlite3.connect("ems_logs.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM dispatch_logs")
            total_dispatches = cursor.fetchone()[0]
            
            if total_dispatches == 0:
                ctk.CTkLabel(self.stats_frame, text="No database records found.", text_color="yellow").pack(pady=20)
                conn.close()
                return

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

    def export_csv(self):
        try:
            conn = sqlite3.connect("ems_logs.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispatch_logs")
            rows = cursor.fetchall()
            
            with open("dispatch_report.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([i[0] for i in cursor.description])
                writer.writerows(rows)
                
            conn.close()
            self.export_btn.configure(text="Exported Successfully!", fg_color="#10b981")
        except Exception:
            self.export_btn.configure(text="Export Failed", fg_color="red")

    def clear_db(self):
        try:
            conn = sqlite3.connect("ems_logs.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dispatch_logs")
            conn.commit()
            conn.close()
            self.clear_btn.configure(text="Database Cleared", fg_color="#10b981")
            self.load_data()
        except Exception:
            self.clear_btn.configure(text="Clear Failed", fg_color="red")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = AnalyticsWindow()
    app.mainloop()