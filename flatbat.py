#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_battery_status():
    battery = psutil.sensors_battery()
    charge_percentage = battery.percent if battery else 0
    is_charging = battery.power_plugged if battery else False

    # Determine bar color based on battery percentage
    if charge_percentage < 15:
        bar_color = "#FF0000"  # Red
    elif charge_percentage < 30:
        bar_color = "#FF00FF"  # Pink
    else:
        bar_color = "#00FF00" if not is_charging else "#00FFFF"  # Green or Cyan

    # Calculate bar dimensions
    screen_width = root.winfo_screenwidth()
    bar_width = int(screen_width * (charge_percentage / 100))
    bar_center = (screen_width - bar_width) // 2  # Center the bar horizontally

    # Update the bar for battery usage
    battery_bar.place(x=bar_center, y=0, width=bar_width, height=2)
    battery_bar.config(bg=bar_color)

    # Update unused area (black)
    unused_bar.place(x=0, y=0, width=screen_width, height=2)
    unused_bar.lower()  # Ensure unused bar is behind the battery bar

    # Refresh every 20 seconds
    root.after(20000, update_battery_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
root.geometry(f"{root.winfo_screenwidth()}x2+0+{root.winfo_screenheight() - 2}")  # Bottom 2px
root.attributes("-topmost", True)  # Always on top

# Create bars
unused_bar = tk.Label(root, bg="#000000")  # Black for unused space
battery_bar = tk.Label(root)  # Color for battery level

# Update initial status
update_battery_status()

# Start event loop
root.mainloop()
