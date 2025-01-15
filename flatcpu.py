#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_cpu_status():
    cpu_percentage = psutil.cpu_percent(interval=0.5)

    # Calculate height for the CPU usage bar
    used_height = int(screen_height * (cpu_percentage / 100))
    unused_height = screen_height - used_height
    center_position = (screen_height - used_height) // 2  # Center the active bar vertically

    # Update the "used" portion (red for active)
    used_bar.place(x=0, y=center_position, width=4, height=used_height)
    used_bar.config(bg="#FF0000")  # Red for CPU usage

    # Update the "unused" portion (black for inactive)
    unused_bar.place(x=0, y=0, width=4, height=screen_height)
    unused_bar.lower()  # Ensure unused bar is behind the active bar

    # Refresh every 1 second
    root.after(1000, update_cpu_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Position the window at the left center of the screen
root.geometry(f"4x{screen_height}+0+0")
root.attributes("-topmost", True)  # Always on top

# Create the bars for CPU usage
unused_bar = tk.Label(root, bg="#000000")  # Black for inactive CPU area
used_bar = tk.Label(root)  # Red for active CPU usage

# Update initial status
update_cpu_status()

# Start event loop
root.mainloop()
