import customtkinter as ctk
import subprocess
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EMS Dispatch Command - Auth")
        self.geometry("400x350")
        
        self.label = ctk.CTkLabel(self, text="EMS Dispatcher Login", font=("Arial", 20, "bold"))
        self.label.pack(pady=30)
        
        self.username = ctk.CTkEntry(self, placeholder_text="Username (admin)")
        self.username.pack(pady=10)
        
        self.password = ctk.CTkEntry(self, placeholder_text="Password (admin123)", show="*")
        self.password.pack(pady=10)
        
        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_btn.pack(pady=20)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()

    def login(self):
        if self.username.get() == "admin" and self.password.get() == "admin123":
            self.error_label.configure(text="")
            self.show_dashboard_menu()
        else:
            self.error_label.configure(text="Invalid credentials")
            
    def show_dashboard_menu(self):
        self.username.pack_forget()
        self.password.pack_forget()
        self.login_btn.pack_forget()
        
        self.label.configure(text="Main Menu")
        
        ctk.CTkButton(self, text="Launch Live Simulation", command=lambda: subprocess.Popen([sys.executable, "ems_dispatcher.py"])).pack(pady=10)
        ctk.CTkButton(self, text="View Analytics", command=lambda: subprocess.Popen([sys.executable, "analytics.py"]), fg_color="#10b981", hover_color="#059669").pack(pady=10)

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()