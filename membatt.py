#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_status():
    # Battery status
    battery = psutil.sensors_battery()
    charge_percentage = battery.percent
    is_charging = battery.power_plugged
    
    # Colors for battery bar
    charged_color = "#00FF00" if not is_charging else "#00FFFF"  # Green or Cyan
    # If battery is below 15%, the uncharged section turns red
    uncharged_color = "#FF0000" if charge_percentage < 15 else ("#FF0000" if not is_charging else "#FF00FF")  # Red if <15%, otherwise Red/Magenta
    
    # Screen width
    screen_width = root.winfo_screenwidth()
    
    # Widths for battery bar
    charged_width = int(screen_width * (charge_percentage / 100))
    uncharged_width = screen_width - charged_width
    
    # Update battery bar
    charged_bar.place(x=0, y=0, width=charged_width, height=3)
    charged_bar.config(bg=charged_color)
    
    uncharged_bar.place(x=charged_width, y=0, width=uncharged_width, height=3)
    uncharged_bar.config(bg=uncharged_color)
    
    # Memory status
    memory = psutil.virtual_memory()
    memory_used_percentage = memory.percent
    
    # Colors for memory bar
    memory_used_color = "#0000FF" if memory_used_percentage < 90 else "#FFA500"  # Blue, or Orange if >=90%
    memory_free_color = "#808080"  # Gray for free memory
    
    # Widths for memory bar
    memory_used_width = int(screen_width * (memory_used_percentage / 100))
    memory_free_width = screen_width - memory_used_width
    
    # Update memory bar
    memory_used_bar.place(x=0, y=3, width=memory_used_width, height=3)
    memory_used_bar.config(bg=memory_used_color)
    
    memory_free_bar.place(x=memory_used_width, y=3, width=memory_free_width, height=3)
    memory_free_bar.config(bg=memory_free_color)
    
    # Refresh every 20 seconds
    root.after(20000, update_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
root.geometry(f"{root.winfo_screenwidth()}x6+0+0")  # Set to screen width and 6px height (3px per line)
root.attributes("-topmost", True)  # Always on top

# Create bars for battery and memory
charged_bar = tk.Label(root)
uncharged_bar = tk.Label(root)
memory_used_bar = tk.Label(root)
memory_free_bar = tk.Label(root)

# Update initial status
update_status()

# Start event loop
root.mainloop()

