#!/usr/bin/env python3
import tkinter as tk
import psutil

def update_memory_status():
    memory = psutil.virtual_memory()
    memory_used_percentage = memory.percent

    # Get screen dimensions
    screen_height = root.winfo_screenheight()

    # Calculate height for the used memory bar
    used_height = int(screen_height * (memory_used_percentage / 100))
    center_position = (screen_height - used_height) // 2  # Center the bar vertically

    # Update the "used" portion (blue for active memory)
    used_bar.place(x=0, y=center_position, width=2, height=used_height)
    used_bar.config(bg="#0000FF")  # Blue for memory usage

    # Update the "unused" portion (black for free memory)
    unused_bar.place(x=0, y=0, width=2, height=screen_height)
    unused_bar.lower()  # Ensure the unused bar is behind the used bar

    # Refresh every 1 second
    root.after(1000, update_memory_status)

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # No borders
root.geometry(f"2x{root.winfo_screenheight()}+{root.winfo_screenwidth() - 2}+0")  # Right 2px
root.attributes("-topmost", True)  # Always on top

# Create the bars for memory usage
unused_bar = tk.Label(root, bg="#000000")  # Black for free memory
used_bar = tk.Label(root)  # Blue for active memory

# Update initial status
update_memory_status()

# Start event loop
root.mainloop()
