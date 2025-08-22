#!/usr/bin/env python3
import sys
import tkinter as tk
import psutil

# Variables for pulsing effect
pulse_color_index = 0
pulse_colors = ["#FF9999", "#FF6666", "#FF3333", "#FF0000", "#FF3333", "#FF6666", "#FF9999"]

def update_status():
    global pulse_color_index

    # Screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Battery status
    battery = psutil.sensors_battery()
    charge_percentage = battery.percent if battery else 0
    is_charging = battery.power_plugged if battery else False

    # Battery colors
    if charge_percentage < 12:
        uncharged_color = pulse_colors[pulse_color_index]
        pulse_color_index = (pulse_color_index + 1) % len(pulse_colors)
    else:
        uncharged_color = "#FF0000" if not is_charging else "#FF00FF"

    charged_color = "#00FF00" if not is_charging else "#00FFFF"

    # Memory status
    memory = psutil.virtual_memory()
    memory_used_percentage = memory.percent
    memory_used_color = "#0000FF" if memory_used_percentage < 90 else "#FFA500"
    memory_free_color = "#808080"

    # CPU status
    cpu_used_percentage = psutil.cpu_percent(interval=None)
    cpu_used_color = "#FFA500"
    cpu_free_color = "#808080"

    # Battery bar at bottom (1 pixel height)
    battery_bar_height = 1
    charged_width = int(screen_width * (charge_percentage / 100))
    uncharged_width = screen_width - charged_width

    charged_bar.place(x=0, y=screen_height - battery_bar_height, width=charged_width, height=battery_bar_height)
    charged_bar.config(bg=charged_color)

    uncharged_bar.place(x=charged_width, y=screen_height - battery_bar_height, width=uncharged_width, height=battery_bar_height)
    uncharged_bar.config(bg=uncharged_color)

    # CPU on left (1-pixel width)
    cpu_bar_width = 1
    cpu_used_height = int(screen_height * (cpu_used_percentage / 100))
    cpu_free_height = screen_height - cpu_used_height

    cpu_used_bar.place(x=0, y=0, width=cpu_bar_width, height=cpu_used_height)
    cpu_used_bar.config(bg=cpu_used_color)

    cpu_free_bar.place(x=0, y=cpu_used_height, width=cpu_bar_width, height=cpu_free_height)
    cpu_free_bar.config(bg=cpu_free_color)

    # Memory on right (1-pixel width)
    mem_bar_width = 1
    memory_used_height = int(screen_height * (memory_used_percentage / 100))
    memory_free_height = screen_height - memory_used_height

    memory_used_bar.place(x=screen_width - mem_bar_width, y=0, width=mem_bar_width, height=memory_used_height)
    memory_used_bar.config(bg=memory_used_color)

    memory_free_bar.place(x=screen_width - mem_bar_width, y=memory_used_height, width=mem_bar_width, height=memory_free_height)
    memory_free_bar.config(bg=memory_free_color)

    # Refresh every second
    root.after(1000, update_status)

root = tk.Tk()
root.overrideredirect(True)  # No borders
root.attributes("-topmost", True)  # Always on top

# Only show the 1-pixel-wide/high bars
root.geometry(f"{1}x{1}+0+0")
root.configure(bg="black")  # Background for visual clarity

# Create bars for battery, memory, CPU
charged_bar = tk.Label(root)
uncharged_bar = tk.Label(root)

memory_used_bar = tk.Label(root)
memory_free_bar = tk.Label(root)

cpu_used_bar = tk.Label(root)
cpu_free_bar = tk.Label(root)

# Update initial status
update_status()

# Start event loop
root.mainloop()
