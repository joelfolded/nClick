import customtkinter as ctk
import pyautogui
import keyboard
import threading
import time
from tkinter import messagebox

class AutoClicker:
    def __init__(self):
        self.clicking = False
        self.click_thread = None
        self.hotkey = 'f6'
        
    def start_clicking(self, cps, button, click_type, max_clicks, position_lock, position):
        click_count = 0
        interval = 1.0 / cps
        
        while self.clicking:
            if max_clicks > 0 and click_count >= max_clicks:
                self.clicking = False
                break
                
            if position_lock and position:
                pyautogui.click(position[0], position[1], button=button, clicks=click_type)
            else:
                pyautogui.click(button=button, clicks=click_type)
            
            click_count += 1
            time.sleep(interval)
    
    def toggle_clicking(self, cps, button, click_type, max_clicks, position_lock, position):
        if not self.clicking:
            self.clicking = True
            self.click_thread = threading.Thread(
                target=self.start_clicking,
                args=(cps, button, click_type, max_clicks, position_lock, position),
                daemon=True
            )
            self.click_thread.start()
        else:
            self.clicking = False

class nClickGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = ctk.CTk()
        self.root.title("nClick - Auto Clicker")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        self.clicker = AutoClicker()
        self.position_lock = False
        self.saved_position = None
        
        self.create_widgets()
        self.setup_hotkey()
        
    def create_widgets(self):
        title = ctk.CTkLabel(
            self.root,
            text="nClick Auto Clicker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        cps_label = ctk.CTkLabel(main_frame, text="Clicks per Second (CPS):", font=ctk.CTkFont(size=14))
        cps_label.pack(pady=(20, 5))
        
        self.cps_slider = ctk.CTkSlider(main_frame, from_=1, to=100, number_of_steps=99)
        self.cps_slider.set(10)
        self.cps_slider.pack(pady=5)
        
        self.cps_value = ctk.CTkLabel(main_frame, text="10 CPS", font=ctk.CTkFont(size=12))
        self.cps_value.pack(pady=5)
        self.cps_slider.configure(command=self.update_cps_label)
        
        button_label = ctk.CTkLabel(main_frame, text="Mouse Button:", font=ctk.CTkFont(size=14))
        button_label.pack(pady=(15, 5))
        
        self.button_var = ctk.StringVar(value="left")
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=5)
        
        ctk.CTkRadioButton(
            button_frame,
            text="Left",
            variable=self.button_var,
            value="left"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            button_frame,
            text="Right",
            variable=self.button_var,
            value="right"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            button_frame,
            text="Middle",
            variable=self.button_var,
            value="middle"
        ).pack(side="left", padx=10)
        
        click_type_label = ctk.CTkLabel(main_frame, text="Click Type:", font=ctk.CTkFont(size=14))
        click_type_label.pack(pady=(15, 5))
        
        self.click_type_var = ctk.StringVar(value="1")
        click_type_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["Single Click", "Double Click"],
            variable=self.click_type_var,
            command=self.update_click_type
        )
        click_type_menu.pack(pady=5)
        
        max_clicks_label = ctk.CTkLabel(main_frame, text="Max Clicks (0 = unlimited):", font=ctk.CTkFont(size=14))
        max_clicks_label.pack(pady=(15, 5))
        
        self.max_clicks_entry = ctk.CTkEntry(main_frame, placeholder_text="0")
        self.max_clicks_entry.pack(pady=5)
        self.max_clicks_entry.insert(0, "0")
        
        position_label = ctk.CTkLabel(main_frame, text="Position:", font=ctk.CTkFont(size=14))
        position_label.pack(pady=(15, 5))
        
        self.position_switch = ctk.CTkSwitch(
            main_frame,
            text="Lock Current Position",
            command=self.toggle_position_lock
        )
        self.position_switch.pack(pady=5)
        
        self.position_info = ctk.CTkLabel(main_frame, text="Position: Follow Cursor", font=ctk.CTkFont(size=11))
        self.position_info.pack(pady=5)
        
        hotkey_label = ctk.CTkLabel(main_frame, text="Hotkey:", font=ctk.CTkFont(size=14))
        hotkey_label.pack(pady=(15, 5))
        
        self.hotkey_display = ctk.CTkLabel(
            main_frame,
            text=f"Press {self.clicker.hotkey.upper()} to Start/Stop",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff00"
        )
        self.hotkey_display.pack(pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.root,
            text="Status: Stopped",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ff0000"
        )
        self.status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start (F6)",
            command=self.manual_toggle,
            fg_color="#00aa00",
            hover_color="#00dd00",
            width=140
        )
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self.stop_clicking,
            fg_color="#aa0000",
            hover_color="#dd0000",
            width=140,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
    def update_cps_label(self, value):
        self.cps_value.configure(text=f"{int(value)} CPS")
    
    def update_click_type(self, choice):
        if choice == "Single Click":
            self.click_type_var.set("1")
        else:
            self.click_type_var.set("2")
    
    def toggle_position_lock(self):
        self.position_lock = self.position_switch.get()
        if self.position_lock:
            self.saved_position = pyautogui.position()
            self.position_info.configure(
                text=f"Position: Locked at ({self.saved_position[0]}, {self.saved_position[1]})"
            )
        else:
            self.saved_position = None
            self.position_info.configure(text="Position: Follow Cursor")
    
    def setup_hotkey(self):
        keyboard.on_press_key(self.clicker.hotkey, lambda _: self.manual_toggle())
    
    def manual_toggle(self):
        if not self.clicker.clicking:
            self.start_clicking()
        else:
            self.stop_clicking()
    
    def start_clicking(self):
        try:
            cps = int(self.cps_slider.get())
            button = self.button_var.get()
            click_type = int(self.click_type_var.get())
            max_clicks = int(self.max_clicks_entry.get())
            
            if cps < 1 or cps > 1000:
                messagebox.showerror("Error", "CPS must be between 1 and 1000!")
                return
            
            self.clicker.toggle_clicking(
                cps, button, click_type, max_clicks,
                self.position_lock, self.saved_position
            )
            
            self.status_label.configure(text="Status: Running", text_color="#00ff00")
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def stop_clicking(self):
        self.clicker.clicking = False
        self.status_label.configure(text="Status: Stopped", text_color="#ff0000")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = nClickGUI()
    app.run()