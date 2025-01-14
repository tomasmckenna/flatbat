#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_battery_status():
    battery = psutil.sensors_battery()
    charge_percentage = battery.percent
    is_charging = battery.power_plugged
    
    # Colors reflect charging state
    charged_color = "#00FF00" if not is_charging else "#00FFFF"  # Green or Cyan
    uncharged_color = "#FF0000" if not is_charging else "#FF00FF"  # Red or Magenta
    
    # Get screen width
    screen_width = root.winfo_screenwidth()

    # Calculate width for charged and uncharged sections
    charged_width = int(screen_width * (charge_percentage / 100))
    uncharged_width = screen_width - charged_width
    
    # Update the size of the "charged" and "uncharged" portions
    charged_bar.place(x=0, y=0, width=charged_width, height=2)
    charged_bar.config(bg=charged_color)
    
    uncharged_bar.place(x=charged_width, y=0, width=uncharged_width, height=2)
    uncharged_bar.config(bg=uncharged_color)
    
    # Refresh every 20 seconds
    root.after(20000, update_battery_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
root.geometry(f"{root.winfo_screenwidth()}x2+0+{root.winfo_screenheight() - 2}")  # Bottom 2px
root.attributes("-topmost", True)  # Always on top

# Create charged & uncharged bars
charged_bar = tk.Label(root)
uncharged_bar = tk.Label(root)

# Update initial status
update_battery_status()

# Start event loop
root.mainloop()
