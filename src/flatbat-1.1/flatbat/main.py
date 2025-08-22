#!/usr/bin/env python3
import tkinter as tk
import psutil
import threading
import datetime
import math
import yaml
import os

CONFIG_PATH = os.path.expanduser("~/.config/flatbat/config.yaml")

DEFAULT_CONFIG = {
    'general': {
        'batt': True,
        'clock': False,
        'cpu': True,
        'gpu': True,
        'mem': True,
    },
    'batt': {
        'unplugged': '#004442',
        'plugged': '#11ff11',
    },
    'clock': {
        'hour': '#ff0000',
        'min': '#0000ff',
    },
    'cpu': {
        'colour': '#ff0000',
    },
    'gpu': {
        'colour': '#ffff00',
    },
    'mem': {
        'colour': '#0000ff',
    },
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG
    else:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)

def run_combined():
    config = load_config() 
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    bar_width = 3
    hand_length = 44
    hand_width = 3
# second_hand_length = 4
# second_hand_width = 3

 # Windows setup
    if config['general'].get('gpu', True) or config['general'].get('clock', False):
        gpu_window = tk.Toplevel(root)
        gpu_window.overrideredirect(True)
        gpu_window.geometry(f"{screen_width}x{bar_width}+0+0")
        gpu_window.attributes("-topmost", True)
        gpu_canvas = tk.Canvas(gpu_window, width=screen_width, height=bar_width, bg="black", highlightthickness=0)
        gpu_canvas.pack()
        gpu_color = config.get('gpu', {}).get('colour', '#800080')

    if config['general'].get('cpu', True) or config['general'].get('clock', False):
        cpu_window = tk.Toplevel(root)
        cpu_window.overrideredirect(True)
        cpu_window.geometry(f"{bar_width}x{screen_height}+0+0")
        cpu_window.attributes("-topmost", True)
        cpu_canvas = tk.Canvas(cpu_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
        cpu_canvas.pack()
        cpu_color = config.get('cpu', {}).get('colour', '#FF0000')

    if config['general'].get('mem', True) or config['general'].get('clock', False):
        memory_window = tk.Toplevel(root)
        memory_window.overrideredirect(True)
        memory_window.geometry(f"{bar_width}x{screen_height}+{screen_width - bar_width}+0")
        memory_window.attributes("-topmost", True)
        memory_canvas = tk.Canvas(memory_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
        memory_canvas.pack()
        mem_color = config.get('mem', {}).get('colour', '#0000FF')

    if config['general'].get('batt', True) or config['general'].get('clock', False):
        battery_window = tk.Toplevel(root)
        battery_window.overrideredirect(True)
        battery_window.geometry(f"{screen_width}x2+0+{screen_height - 2}")
        battery_window.attributes("-topmost", True)
        battery_canvas = tk.Canvas(battery_window, width=screen_width, height=2, bg="black", highlightthickness=0)
        battery_canvas.pack()

    def update_gpu():
        if not config['general'].get('gpu', True): return
        gpu_temp = 0
        temperatures = psutil.sensors_temperatures()
        if "amdgpu" in temperatures:
            gpu_temp = temperatures["amdgpu"][0].current
        elif "nvme" in temperatures:
            gpu_temp = temperatures["nvme"][0].current

        gpu_usage = int(gpu_temp / 100 * screen_width)
        gpu_canvas.delete("all")
        gpu_canvas.create_rectangle((screen_width - gpu_usage) // 2, 0, (screen_width + gpu_usage) // 2, bar_width, fill=gpu_color, outline='')
        root.after(5000, update_gpu)

    def update_cpu_memory():
        if config['general'].get('cpu', True):
            cpu_percentage = psutil.cpu_percent(interval=0.5)
            cpu_height = int(screen_height * (cpu_percentage / 100))
            cpu_canvas.delete("all")
            if cpu_height > 0:
                cpu_canvas.create_rectangle(0, (screen_height - cpu_height) // 2, bar_width, (screen_height + cpu_height) // 2, fill=cpu_color, outline='')

        if config['general'].get('mem', True):
            memory = psutil.virtual_memory()
            memory_height = int(screen_height * (memory.percent / 100))
            memory_canvas.delete("all")
            if memory_height > 0:
                memory_canvas.create_rectangle(0, (screen_height - memory_height) // 2, bar_width, (screen_height + memory_height) // 2, fill=mem_color, outline='')

        if config['general'].get('clock', False):
            draw_clock()

        root.after(1000, update_cpu_memory)

    def update_battery():
        if not config['general'].get('batt', True): return
        battery = psutil.sensors_battery()
        charge_percentage = battery.percent if battery else 0
        is_charging = battery.power_plugged if battery else False

        color_config = config.get('batt', {})
        if is_charging:
            bar_color = color_config.get('plugged', '#00FFFF')
        else:
            bar_color = color_config.get('unplugged', '#00FFFF')

        battery_width = int(screen_width * (charge_percentage / 100))
        battery_canvas.delete("all")
        battery_canvas.create_rectangle((screen_width - battery_width) // 2, 0, (screen_width + battery_width) // 2, 2, fill=bar_color, outline='')
        root.after(20000, update_battery)

    def draw_clock():
        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute

        hour_angle = (hour * 30 + minute * 0.5)  # 12:00 = 0°
        minute_angle = minute * 6

        for angle in range(0, 360, 30):
            draw_hour_marker(angle, "gray")

        draw_hand(hour_angle, config.get('clock', {}).get('hour', '#00FF00'), hand_length, hand_width)
        draw_hand(minute_angle, config.get('clock', {}).get('min', '#FFD700'), hand_length, hand_width)

    def draw_hour_marker(angle, color):
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        if edge == "top" and (config['general'].get('gpu', True) or config['general'].get('clock', False)):
            gpu_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "bottom" and (config['general'].get('batt', True) or config['general'].get('clock', False)):
            battery_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "left" and (config['general'].get('cpu', True) or config['general'].get('clock', False)):
            cpu_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')
        elif edge == "right" and (config['general'].get('mem', True) or config['general'].get('clock', False)):
            memory_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')

    def draw_hand(angle, color, length, width):
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        if edge == "top" and (config['general'].get('gpu', True) or config['general'].get('clock', False)):
            gpu_canvas.create_rectangle(max(0, x - length // 2), 0, min(screen_width, x + length // 2), width, fill=color, outline='')
        elif edge == "bottom" and (config['general'].get('batt', True) or config['general'].get('clock', False)):
            battery_canvas.create_rectangle(max(0, x - length // 2), 0, min(screen_width, x + length // 2), width, fill=color, outline='')
        elif edge == "left" and (config['general'].get('cpu', True) or config['general'].get('clock', False)):
            cpu_canvas.create_rectangle(0, max(0, y - length // 2), width, min(screen_height, y + length // 2), fill=color, outline='')
        elif edge == "right" and (config['general'].get('mem', True) or config['general'].get('clock', False)):
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

    if config['general'].get('gpu', True):
        threading.Thread(target=update_gpu).start()
    if config['general'].get('cpu', True) or config['general'].get('mem', True) or config['general'].get('clock', False):
        threading.Thread(target=update_cpu_memory).start()
    if config['general'].get('batt', True):
        threading.Thread(target=update_battery).start()

    root.mainloop()

if __name__ == "__main__":
    run_combined()