#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_cpu_status():
    cpu_percentage = psutil.cpu_percent(interval=0.5)

    # Calculate height for the CPU usage bar
    used_height = int(screen_height * (cpu_percentage / 100))
    center_position = (screen_height - used_height) // 2  # Center the bar vertically

    # Update the size and position of the "used" portion
    if used_height > 0:
        used_bar.place(x=0, y=center_position, width=4, height=used_height)
        used_bar.config(bg="#FFA500")  # Orange color for CPU usage
    else:
        used_bar.place_forget()  # Hide the bar if usage is zero

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

# Create the bar for used CPU
used_bar = tk.Label(root)

# Update initial status
update_cpu_status()

# Start event loop
root.mainloop()
