#!/usr/bin/env python3
import tkinter as tk
import psutil
import threading

# Battery Visualization
def run_battery():
    def update_battery_status():
        battery = psutil.sensors_battery()
        charge_percentage = battery.percent if battery else 0
        is_charging = battery.power_plugged if battery else False

        if not is_charging:
            bar_color = '#00FFFF'
        else:
            # Determine bar color based on battery percentage
            if charge_percentage < 15:
                bar_color = "#FF0000"  # Red
            elif charge_percentage < 30:
                bar_color = "#FF00FF"  # Pink
            else:
                bar_color = "#00FFFF"  # Green or Cyan

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

# CPU Visualization
def run_cpu():
    def update_cpu_status():
        cpu_percentage = psutil.cpu_percent(interval=0.5)
        used_height = int(screen_height * (cpu_percentage / 100))
        center_position = (screen_height - used_height) // 2  # Center the bar vertically

        if used_height > 0:
            used_bar.place(x=0, y=center_position, width=4, height=used_height)
            used_bar.config(bg="#FF0000")  # Red for CPU usage
        else:
            used_bar.place(x=0, y=screen_height // 2, width=4, height=1)  # Minimum visibility

        # Black for unused space
        unused_bar.place(x=0, y=0, width=4, height=screen_height)
        unused_bar.lower()  # Ensure unused bar is behind the used bar

        root.after(1000, update_cpu_status)

    root = tk.Tk()
    root.overrideredirect(True)  # No borders
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry(f"4x{screen_height}+0+0")
    root.attributes("-topmost", True)  # Always on top

    used_bar = tk.Label(root)
    unused_bar = tk.Label(root, bg="#000000")  # Black for unused area
    update_cpu_status()
    root.mainloop()

# Memory Visualization
def run_memory():
    def update_memory_status():
        memory = psutil.virtual_memory()
        memory_used_percentage = memory.percent

        used_height = int(screen_height * (memory_used_percentage / 100))
        center_position = (screen_height - used_height) // 2  # Center the bar vertically

        if used_height > 0:
            used_bar.place(x=0, y=center_position, width=4, height=used_height)
            used_bar.config(bg="#0000FF")  # Blue for memory usage
        else:
            used_bar.place(x=0, y=screen_height // 2, width=4, height=1)  # Minimum visibility

        # Black for unused space
        unused_bar.place(x=0, y=0, width=4, height=screen_height)
        unused_bar.lower()  # Ensure unused bar is behind the used bar

        root.after(1000, update_memory_status)

    root = tk.Tk()
    root.overrideredirect(True)  # No borders
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Place at right side of screen
    root.geometry(f"4x{screen_height}+{screen_width-4}+0")
    root.attributes("-topmost", True)  # Always on top

    used_bar = tk.Label(root)
    unused_bar = tk.Label(root, bg="#000000")  # Black for unused area
    update_memory_status()
    root.mainloop()

# Run all components using threads
if __name__ == "__main__":
    threading.Thread(target=run_battery).start()
    threading.Thread(target=run_cpu).start()
    threading.Thread(target=run_memory).start()
