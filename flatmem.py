#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_memory_status():
    memory = psutil.virtual_memory()
    memory_used_percentage = memory.percent
    
    # Colors reflect memory usage
    used_color = "#0000FF"  # Blue
    free_color = "#808080"  # Gray
    
    # Get screen height
    screen_height = root.winfo_screenheight()

    # Calculate height for used and free portions
    used_height = int(screen_height * (memory_used_percentage / 100))
    free_height = screen_height - used_height
    
    # Update the size of the "used" and "free" portions
    used_bar.place(x=0, y=0, width=2, height=used_height)
    used_bar.config(bg=used_color)
    
    free_bar.place(x=0, y=used_height, width=2, height=free_height)
    free_bar.config(bg=free_color)
    
    # Refresh every 1 second
    root.after(1000, update_memory_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
root.geometry(f"2x{root.winfo_screenheight()}+{root.winfo_screenwidth() - 2}+0")  # Right 2px
root.attributes("-topmost", True)  # Always on top

# Create used & free bars
used_bar = tk.Label(root)
free_bar = tk.Label(root)

# Update initial status
update_memory_status()

# Start event loop
root.mainloop()
