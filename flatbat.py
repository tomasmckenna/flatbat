#!/usr/bin/env python3
import os
os.environ["GDK_BACKEND"] = "wayland"

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import psutil
import yaml
import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".config" / "flatbat" / "config.yaml"

DEFAULTS = {
    "general": {"gpu": False, "cpu": False, "mem": False, "batt": True, "clock": True, "overlay": True, "gaps": 5},
    "gpu":  {"colour": "#800080", "thickness": 5},
    "cpu":  {"colour": "#FF0000", "thickness": 3},
    "mem":  {"colour": "#3333FF", "thickness": 6},
    "batt": {"critical_battery_level": 20, "critical_battery_color": "#FF0000",
             "plugged": "#00FFF0", "unplugged": "#00FF00", "empty": "#580000", "thickness": 2},
    "clock": {"hour": "#228844", "min": "#994A99", "segments": "#0000FF", "current": "#00F0F0", "thickness": 4},
}
def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULTS, f, default_flow_style=False)
        return DEFAULTS
    with open(CONFIG_PATH) as f:
        user = yaml.safe_load(f) or {}
    # Deep merge user over defaults
    cfg = {}
    for key, val in DEFAULTS.items():
        if isinstance(val, dict):
            cfg[key] = {**val, **(user.get(key) or {})}
        else:
            cfg[key] = user.get(key, val)
    return cfg

# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def draw_fill_bar(cr, width, height, fill_frac, fill_color, empty_color):
    filled = int(width * max(0.0, min(1.0, fill_frac)))
    cr.set_source_rgb(*fill_color)
    cr.rectangle(0, 0, filled, height)
    cr.fill()
    cr.set_source_rgb(*empty_color)
    cr.rectangle(filled, 0, width - filled, height)
    cr.fill()

# ── State ─────────────────────────────────────────────────────────────────────

state = {}

def refresh_state(cfg):
    g = cfg["general"]

    if g.get("cpu"):
        state["cpu"] = psutil.cpu_percent(interval=None) / 100.0

    if g.get("mem"):
        state["mem"] = psutil.virtual_memory().percent / 100.0

    if g.get("batt"):
        bat = psutil.sensors_battery()
        if bat:
            state["batt_pct"]      = bat.percent / 100.0
            state["batt_plugged"]  = bat.power_plugged
        else:
            state["batt_pct"]      = 1.0
            state["batt_plugged"]  = True

    if g.get("clock"):
        now = datetime.datetime.now()
        state["hour_frac"] = now.hour / 23.0
        state["min_frac"]  = now.minute / 59.0

# ── Draw ──────────────────────────────────────────────────────────────────────

def make_draw_cb(cfg, bars, gaps):
    """Return a draw callback that renders all enabled bars top-to-bottom."""
    def on_draw(widget, cr):
        width = widget.get_allocated_width()
        y = 0
        for idx, (name, thickness) in enumerate(bars):
            if name == "cpu":
                c = cfg["cpu"]
                fill  = hex_to_rgb(c["colour"])
                empty = (0.1, 0.1, 0.1)
                cr.save(); cr.translate(0, y)
                draw_fill_bar(cr, width, thickness, state.get("cpu", 0), fill, empty)
                cr.restore()

            elif name == "mem":
                c = cfg["mem"]
                fill  = hex_to_rgb(c["colour"])
                empty = (0.1, 0.1, 0.1)
                cr.save(); cr.translate(0, y)
                draw_fill_bar(cr, width, thickness, state.get("mem", 0), fill, empty)
                cr.restore()

            elif name == "batt":
                c   = cfg["batt"]
                pct = state.get("batt_pct", 1.0)
                empty_col = hex_to_rgb(c.get("empty", "#580000"))
                if state.get("batt_plugged"):
                    fill_col = hex_to_rgb(c["plugged"])
                elif pct <= c["critical_battery_level"] / 100.0:
                    fill_col = hex_to_rgb(c["critical_battery_color"])
                else:
                    fill_col = hex_to_rgb(c["unplugged"])
                cr.save(); cr.translate(0, y)
                draw_fill_bar(cr, width, thickness, pct, fill_col, empty_col)
                cr.restore()

            elif name == "clock":
                c           = cfg["clock"]
                hour_col    = hex_to_rgb(c["hour"])
                min_col     = hex_to_rgb(c["min"])
                seg_col     = hex_to_rgb(c.get("segments", "#444444"))
                cur_col     = hex_to_rgb(c.get("current", "#00F0F0"))
                empty_col   = (0.1, 0.1, 0.1)
                gap         = 1   # px gap between normal segments
                big_gap     = 7   # px gap at 3rd, 6th, 9th positions

                now          = datetime.datetime.now()
                cur_hour     = now.hour % 12   # current hour segment index
                cur_min_seg  = now.minute // 5 # current minute segment index

                half = width // 2

                def draw_subdivided(cx, cy, sw, th, filled_subs):
                    """Draw a segment split into 5 sub-parts; filled_subs of them lit in cur_col."""
                    sub_w = sw / 5
                    for s in range(5):
                        sx  = int(cx + s * sub_w)
                        snx = int(cx + (s + 1) * sub_w)
                        col = cur_col if s < filled_subs else empty_col
                        cr.set_source_rgb(*col)
                        cr.rectangle(sx, cy, snx - sx, th)
                        cr.fill()

                # ── Hour segments (left half, 12 segments) ──
                # current segment subdivided by how many 12-min chunks into this hour
                hour_subs   = now.minute // 12  # 0-4
                total_gap_h = 3 * big_gap + 8 * gap
                seg_w_h     = (half - total_gap_h) / 12
                x = 0.0
                for i in range(12):
                    sw = max(1, int(seg_w_h))
                    if i < cur_hour:
                        cr.set_source_rgb(*hour_col)
                        cr.rectangle(int(x), y, sw, thickness)
                        cr.fill()
                    elif i == cur_hour:
                        draw_subdivided(int(x), y, sw, thickness, hour_subs)
                    else:
                        cr.set_source_rgb(*empty_col)
                        cr.rectangle(int(x), y, sw, thickness)
                        cr.fill()
                    x += seg_w_h
                    if i < 11:
                        marker = (i + 1) in (3, 6, 9)
                        gw = big_gap if marker else gap
                        cr.set_source_rgb(*(0, 0, 0) if marker else seg_col)
                        cr.rectangle(int(x), y, gw, thickness)
                        cr.fill()
                        x += gw

                # ── Minute segments (right half, 12 segments of 5 min each) ──
                # current segment subdivided by minute-within-the-5-min block
                min_subs    = now.minute % 5   # 0-4
                total_gap_m = 3 * big_gap + 8 * gap
                seg_w_m     = (half - total_gap_m) / 12
                x = float(half)
                for i in range(12):
                    sw = max(1, int(seg_w_m))
                    if i < cur_min_seg:
                        cr.set_source_rgb(*min_col)
                        cr.rectangle(int(x), y, sw, thickness)
                        cr.fill()
                    elif i == cur_min_seg:
                        draw_subdivided(int(x), y, sw, thickness, min_subs)
                    else:
                        cr.set_source_rgb(*empty_col)
                        cr.rectangle(int(x), y, sw, thickness)
                        cr.fill()
                    x += seg_w_m
                    if i < 11:
                        marker = (i + 1) in (3, 6, 9)
                        gw = big_gap if marker else gap
                        cr.set_source_rgb(*(0, 0, 0) if marker else seg_col)
                        cr.rectangle(int(x), y, gw, thickness)
                        cr.fill()
                        x += gw

            y += thickness
            # ── Gap between bars (not after the last one) ──
            if idx < len(bars) - 1 and gaps > 0:
                cr.set_source_rgb(0, 0, 0)
                cr.rectangle(0, y, width, gaps)
                cr.fill()
                y += gaps

    return on_draw

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg  = load_config()
    g    = cfg["general"]
    gaps = int(g.get("gaps", 0))

    # Ordered list of enabled bars (top to bottom)
    ORDER = ["batt", "clock", "mem", "cpu"]
    bars  = [(n, cfg[n]["thickness"]) for n in ORDER if g.get(n)]

    if not bars:
        print("No bars enabled in config — nothing to show.")
        return

    total_height = sum(t for _, t in bars) + gaps * (len(bars) - 1)
    refresh_state(cfg)

    window = Gtk.Window()
    GtkLayerShell.init_for_window(window)
    layer = GtkLayerShell.Layer.OVERLAY if g.get("overlay", True) else GtkLayerShell.Layer.TOP
    GtkLayerShell.set_layer(window, layer)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP,   True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT,  True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.RIGHT, True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.BOTTOM, False)
    GtkLayerShell.set_exclusive_zone(window, total_height)
    window.set_decorated(False)

    geom = Gdk.Geometry()
    geom.min_width  = 1
    geom.max_width  = 100000
    geom.min_height = total_height
    geom.max_height = total_height
    window.set_geometry_hints(None, geom,
        Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE)

    canvas = Gtk.DrawingArea()
    canvas.set_size_request(1, total_height)
    canvas.connect("draw", make_draw_cb(cfg, bars, gaps))
    window.add(canvas)
    window.show_all()

    def update(_):
        refresh_state(cfg)
        canvas.queue_draw()
        return True

    update(None)
    GLib.timeout_add_seconds(2, update, None)
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()