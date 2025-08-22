#!/usr/bin/env python3
import tkinter as tk
import psutil
import threading
import datetime
import math

def run_combined():
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    bar_width = 4
    hand_length = 44
    hand_width = 4
    second_hand_length = 4
    second_hand_width = 4

    # GPU window
    gpu_window = tk.Toplevel(root)
    gpu_window.overrideredirect(True)
    gpu_window.geometry(f"{screen_width}x{bar_width}+0+0")
    gpu_window.attributes("-topmost", True)
    gpu_canvas = tk.Canvas(gpu_window, width=screen_width, height=bar_width, bg="black", highlightthickness=0)
    gpu_canvas.pack()

    # CPU and Memory windows
    cpu_window = tk.Toplevel(root)
    cpu_window.overrideredirect(True)
    cpu_window.geometry(f"{bar_width}x{screen_height}+0+0")
    cpu_window.attributes("-topmost", True)
    cpu_canvas = tk.Canvas(cpu_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
    cpu_canvas.pack()

    memory_window = tk.Toplevel(root)
    memory_window.overrideredirect(True)
    memory_window.geometry(f"{bar_width}x{screen_height}+{screen_width - bar_width}+0")
    memory_window.attributes("-topmost", True)
    memory_canvas = tk.Canvas(memory_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
    memory_canvas.pack()

    # Battery window
    battery_window = tk.Toplevel(root)
    battery_window.overrideredirect(True)
    battery_window.geometry(f"{screen_width}x2+0+{screen_height - 2}")
    battery_window.attributes("-topmost", True)
    battery_canvas = tk.Canvas(battery_window, width=screen_width, height=2, bg="black", highlightthickness=0)
    battery_canvas.pack()

    # GPU Update
    def update_gpu():
        gpu_temp = 0
        temperatures = psutil.sensors_temperatures()
        if "amdgpu" in temperatures:
            gpu_temp = temperatures["amdgpu"][0].current
        elif "nvme" in temperatures:
            gpu_temp = temperatures["nvme"][0].current

        gpu_usage = int(gpu_temp / 100 * screen_width)

        gpu_canvas.delete("all")
        gpu_canvas.create_rectangle((screen_width - gpu_usage) // 2, 0, (screen_width + gpu_usage) // 2, bar_width, fill="#800080", outline='') # Centered

        root.after(5000, update_gpu)

    # CPU and Memory Update
    def update_cpu_memory():
        cpu_percentage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        memory_used_percentage = memory.percent

        cpu_height = int(screen_height * (cpu_percentage / 100))
        memory_height = int(screen_height * (memory_used_percentage / 100))

        cpu_canvas.delete("all")
        if cpu_height > 0:
            cpu_canvas.create_rectangle(0, (screen_height - cpu_height) // 2, bar_width, (screen_height + cpu_height) // 2, fill="#FF0000", outline='')

        memory_canvas.delete("all")
        if memory_height > 0:
            memory_canvas.create_rectangle(0, (screen_height - memory_height) // 2, bar_width, (screen_height + memory_height) // 2, fill="#0000FF", outline='')

        # Draw clock on CPU and Memory
        draw_clock()

        root.after(1000, update_cpu_memory)

    # Battery Update
    def update_battery():
        battery = psutil.sensors_battery()
        charge_percentage = battery.percent if battery else 0
        is_charging = battery.power_plugged if battery else False

        if not is_charging:
            bar_color = '#00FFFF'
        elif charge_percentage < 15:
            bar_color = "#FF0000"
        elif charge_percentage < 30:
            bar_color = "#FF00FF"
        else:
            bar_color = "#00FFFF"

        battery_width = int(screen_width * (charge_percentage / 100))
        battery_canvas.delete("all")
        battery_canvas.create_rectangle((screen_width - battery_width) // 2, 0, (screen_width + battery_width) // 2, 2, fill=bar_color, outline='')
        root.after(20000, update_battery)

    # Clock Draw
    def draw_clock():
        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second

        hour_angle = (hour + minute / 60) * 30
        minute_angle = minute * 6
        second_angle = second * 6

        # Draw hour markers (12, 3, 6, 9)
        for angle in range(0, 360, 30):
            draw_hour_marker(angle, "gray")

        # Draw hour hand
        draw_hand(hour_angle, "#00FF00", hand_length, hand_width)

        # Draw minute hand
        draw_hand(minute_angle, "#FFD700", hand_length, hand_width)

        # Draw second hand
        # draw_hand(second_angle, "#FFD700", second_hand_length, second_hand_width)

        root.after(1000, draw_clock)

    def draw_hour_marker(angle, color):
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        if edge == "top":
            gpu_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "bottom":
            battery_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "left":
            cpu_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')
        elif edge == "right":
            memory_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')

    def draw_hand(angle, color, length, width):
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        if edge == "top":
            gpu_canvas.create_rectangle(max(0, x - length // 2), 0, min(screen_width, x + length // 2), width, fill=color, outline='')
        elif edge == "bottom":
            battery_canvas.create_rectangle(max(0, x - length // 2), 0, min(screen_width, x + length // 2), width, fill=color, outline='')
        elif edge == "left":
            cpu_canvas.create_rectangle(0, max(0, y - length // 2), width, min(screen_height, y + length // 2), fill=color, outline='')
        elif edge == "right":
            memory_canvas.create_rectangle(0, max(0, y - length // 2), width, min(screen_height, y + length // 2), fill=color, outline='')

    def calculate_position(angle, width, height):
        angle = angle % 360
        if 45 <= angle < 135:
            y = int((angle - 45) / 90 * height)
            return width - bar_width, y, "right"
        elif 135 <= angle < 225:
            x = int((225 - angle) / 90 * width)
            return x, height - bar_width, "bottom"
        elif 225 <= angle < 315:
            y = int((315 - angle) / 90 * height)
            return 0, y, "left"
        else:
            x = int((angle if angle < 45 else 360 - angle) / 90 * width)
            return x, 0, "top"

    threading.Thread(target=update_gpu).start()
    threading.Thread(target=update_cpu_memory).start()
    threading.Thread(target=update_battery).start()
    root.mainloop()

if __name__ == "__main__":
    run_combined()