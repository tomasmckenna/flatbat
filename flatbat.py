#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_battery_status():
    battery = psutil.sensors_battery()
    charge_percentage = battery.percent
    is_charging = battery.power_plugged
    
    # colors reflect charging state
    charged_color = "#00FF00" if not is_charging else "#00FFFF"  # Green or Cyan
    uncharged_color = "#FF0000" if not is_charging else "#FF00FF"  # Red or Magenta
    
    # get screen width
    screen_width = root.winfo_screenwidth()

    # calc width for charged and uncharged sections
    charged_width = int(screen_width * (charge_percentage / 100))
    uncharged_width = screen_width - charged_width
    
    # update the size of the "charged" and "uncharged" portions
    charged_bar.place(x=0, y=0, width=charged_width, height=3)
    charged_bar.config(bg=charged_color)
    
    uncharged_bar.place(x=charged_width, y=0, width=uncharged_width, height=3)
    uncharged_bar.config(bg=uncharged_color)
    
    # refresh every 20 seconds
    root.after(20000, update_battery_status)

# create main window
root = tk.Tk()
root.overrideredirect(True)  # no borders
root.geometry(f"{root.winfo_screenwidth()}x3+0+0")  # set to screen width and 3px height
root.attributes("-topmost", True)  # always on top

# create charged & uncharged bars
charged_bar = tk.Label(root)
uncharged_bar = tk.Label(root)

# update initial status
update_battery_status()

# start event loop
root.mainloop()