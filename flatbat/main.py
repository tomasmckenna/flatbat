#!/usr/bin/env python3
import tkinter as tk
import psutil
import datetime
import os
import yaml

CFG_PATH = os.path.expanduser("~/.config/flatbat/config.yaml")

def load_config():
    # Safe defaults that match your sample YAML intent
    default = {
        "general": {"gpu": False, "cpu": True, "mem": True, "batt": True, "clock": False},
        "gpu":  {"colour": "#800080", "thickness": 3},
        "cpu":  {"colour": "#FF0000", "thickness": 3},
        "mem":  {"colour": "#FFF099", "thickness": 3},
        "batt": {"critical_battery_level": 20, "critical_battery_color": "#FF0000",
                 "plugged": "#00FFF0", "unplugged": "#00FF00", "thickness": 3},
        "clock": {"hour": "#00FF00", "min": "#FFD700"},
        "hands": {"length": 44, "width": 3, "second_length": 4, "second_width": 2},
    }
    if not os.path.exists(CFG_PATH):
        return default
    try:
        with open(CFG_PATH, "r") as f:
            cfg = yaml.safe_load(f) or {}
        # shallow merge of provided keys over defaults
        for k, v in default.items():
            if isinstance(v, dict):
                cfg[k] = {**v, **(cfg.get(k) or {})}
            else:
                cfg.setdefault(k, v)
        return cfg
    except Exception:
        return default

CFG = load_config()

def run_combined():
    # Tk init
    root = tk.Tk()
    root.withdraw()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    # Feature toggles
    show_gpu  = bool(CFG["general"].get("gpu", False))
    show_cpu  = bool(CFG["general"].get("cpu", True))
    show_mem  = bool(CFG["general"].get("mem", True))
    show_batt = bool(CFG["general"].get("batt", True))
    show_clk  = bool(CFG["general"].get("clock", False))

    # Thickness (px)
    gpu_th   = int(CFG["gpu"].get("thickness", 3))
    cpu_th   = int(CFG["cpu"].get("thickness", 3))
    mem_th   = int(CFG["mem"].get("thickness", 3))
    batt_th  = int(CFG["batt"].get("thickness", 3))

    # Colors
    gpu_color = CFG["gpu"].get("colour", "#800080")
    cpu_color = CFG["cpu"].get("colour", "#FF0000")
    mem_color = CFG["mem"].get("colour", "#FFF099")
    batt_cfg  = CFG["batt"]
    clk_hour  = CFG["clock"].get("hour", "#00FF00")
    clk_min   = CFG["clock"].get("min", "#FFD700")

    # Clock hands
    hand_len  = int(CFG["hands"].get("length", 44))
    hand_w    = int(CFG["hands"].get("width", 3))
    sec_len   = int(CFG["hands"].get("second_length", 4))
    sec_w     = int(CFG["hands"].get("second_width", 2))

    # Windows & canvases
    gpu_canvas = cpu_canvas = memory_canvas = battery_canvas = None

    if show_gpu:
        gpu_window = tk.Toplevel(root)
        gpu_window.overrideredirect(True)
        gpu_window.geometry(f"{sw}x{gpu_th}+0+0")
        gpu_window.attributes("-topmost", True)
        gpu_canvas = tk.Canvas(gpu_window, width=sw, height=gpu_th, bg="black", highlightthickness=0)
        gpu_canvas.pack()

    if show_cpu:
        cpu_window = tk.Toplevel(root)
        cpu_window.overrideredirect(True)
        cpu_window.geometry(f"{cpu_th}x{sh}+0+0")
        cpu_window.attributes("-topmost", True)
        cpu_canvas = tk.Canvas(cpu_window, width=cpu_th, height=sh, bg="black", highlightthickness=0)
        cpu_canvas.pack()

    if show_mem:
        memory_window = tk.Toplevel(root)
        memory_window.overrideredirect(True)
        memory_window.geometry(f"{mem_th}x{sh}+{sw - mem_th}+0")
        memory_window.attributes("-topmost", True)
        memory_canvas = tk.Canvas(memory_window, width=mem_th, height=sh, bg="black", highlightthickness=0)
        memory_canvas.pack()

    if show_batt:
        battery_window = tk.Toplevel(root)
        battery_window.overrideredirect(True)
        battery_window.geometry(f"{sw}x{batt_th}+0+{sh - batt_th}")
        battery_window.attributes("-topmost", True)
        battery_canvas = tk.Canvas(battery_window, width=sw, height=batt_th, bg="black", highlightthickness=0)
        battery_canvas.pack()

    # Non-blocking CPU baseline
    psutil.cpu_percent(interval=None)

    def update_gpu():
        if not show_gpu: return
        gpu_temp = 0
        try:
            temps = psutil.sensors_temperatures()
            if "amdgpu" in temps and temps["amdgpu"]:
                gpu_temp = temps["amdgpu"][0].current
            elif "nvme" in temps and temps["nvme"]:
                gpu_temp = temps["nvme"][0].current
        except Exception:
            gpu_temp = 0

        gpu_usage = max(0, min(sw, int((gpu_temp / 100.0) * sw)))
        gpu_canvas.delete("all")
        gpu_canvas.create_rectangle((sw - gpu_usage) // 2, 0,
                                    (sw + gpu_usage) // 2, gpu_th,
                                    fill=gpu_color, outline='')
        root.after(5000, update_gpu)

    def update_cpu_mem():
        if show_cpu:
            cpu_pct = psutil.cpu_percent(interval=None)  # non-blocking
            h = int(sh * (cpu_pct / 100.0))
            cpu_canvas.delete("all")
            if h > 0:
                cpu_canvas.create_rectangle(
                    0, (sh - h) // 2,
                    cpu_th, (sh + h) // 2,
                    fill=cpu_color, outline=''
                )

        if show_mem:
            vm = psutil.virtual_memory()
            h = int(sh * (vm.percent / 100.0))
            memory_canvas.delete("all")
            if h > 0:
                memory_canvas.create_rectangle(
                    0, (sh - h) // 2,
                    mem_th, (sh + h) // 2,
                    fill=mem_color, outline=''
                )

        if show_clk:
            draw_clock()

        root.after(1000, update_cpu_mem)

    def update_batt():
        if not show_batt: return
        batt = psutil.sensors_battery()
        pct = int(batt.percent) if batt else 0
        plugged = bool(batt.power_plugged) if batt else False

        crit_lvl = int(batt_cfg.get("critical_battery_level", 20))
        crit_col = batt_cfg.get("critical_battery_color", "#FF0000")
        col = (crit_col if (pct < crit_lvl and not plugged)
               else (batt_cfg.get("plugged", "#00FFF0") if plugged
                     else batt_cfg.get("unplugged", "#00FF00")))

        w = int(sw * (pct / 100.0))
        battery_canvas.delete("all")
        battery_canvas.create_rectangle((sw - w) // 2, 0,
                                        (sw + w) // 2, batt_th,
                                        fill=col, outline='')
        root.after(10000, update_batt)

    def draw_clock():
        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second

        hour_angle = (hour * 30.0 + minute * 0.5)
        minute_angle = minute * 6.0
        second_angle = second * 6.0

        # markers every 30°
        for ang in range(0, 360, 30):
            draw_hour_marker(ang, "gray")

        # hands
        draw_hand(hour_angle,  clk_hour, hand_len, hand_w)
        draw_hand(minute_angle, clk_min,  hand_len, hand_w)
        # Uncomment if you want seconds:
        # draw_hand(second_angle, clk_min, sec_len, sec_w)

    def draw_hour_marker(angle, color):
        x, y, edge = calculate_position(angle, sw, sh)
        if edge == "top" and show_gpu:
            gpu_canvas.create_rectangle(x, 0, x + gpu_th, gpu_th, fill=color, outline='')
        elif edge == "bottom" and show_batt:
            battery_canvas.create_rectangle(x, 0, x + batt_th, batt_th, fill=color, outline='')
        elif edge == "left" and show_cpu:
            cpu_canvas.create_rectangle(0, y, cpu_th, y + cpu_th, fill=color, outline='')
        elif edge == "right" and show_mem:
            memory_canvas.create_rectangle(0, y, mem_th, y + mem_th, fill=color, outline='')

    def draw_hand(angle, color, length, thickness):
        x, y, edge = calculate_position(angle, sw, sh)
        if edge == "top" and show_gpu:
            gpu_canvas.create_rectangle(max(0, x - length // 2), 0,
                                        min(sw, x + length // 2), gpu_th,
                                        fill=color, outline='')
        elif edge == "bottom" and show_batt:
            battery_canvas.create_rectangle(max(0, x - length // 2), 0,
                                            min(sw, x + length // 2), batt_th,
                                            fill=color, outline='')
        elif edge == "left" and show_cpu:
            cpu_canvas.create_rectangle(0, max(0, y - length // 2),
                                        thickness, min(sh, y + length // 2),
                                        fill=color, outline='')
        elif edge == "right" and show_mem:
            memory_canvas.create_rectangle(0, max(0, y - length // 2),
                                           thickness, min(sh, y + length // 2),
                                           fill=color, outline='')

    def calculate_position(angle, width, height):
        angle = angle % 360
        if 45 <= angle < 135:  # right edge (top -> bottom)
            y = int((angle - 45) / 90 * height)
            return width - mem_th, y, "right"
        elif 135 <= angle < 225:  # bottom edge (right -> left)
            x = int((225 - angle) / 90 * width)
            return x, height - batt_th, "bottom"
        elif 225 <= angle < 315:  # left edge (bottom -> top)
            y = int((315 - angle) / 90 * height)
            return 0, y, "left"
        else:  # top edge (left -> right)
            x = int((angle if angle < 45 else 360 - angle) / 90 * width)
            return x, 0, "top"

    # Kick off updates (once each)
    if show_gpu:  update_gpu()
    if show_cpu or show_mem or show_clk: update_cpu_mem()
    if show_batt: update_batt()

    root.mainloop()

if __name__ == "__main__":
    run_combined()
